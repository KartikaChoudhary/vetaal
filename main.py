"""
Entry point of the API. Run it with:
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs to see and test every endpoint
in the browser (FastAPI generates that page for you automatically).
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import engine, get_db
from auth import hash_password, verify_password, create_access_token, get_current_user

# Creates all tables from models.py if they don't already exist.
# (Fine for learning/dev. For a real project you'd use Alembic migrations instead,
# so schema changes are tracked and reversible.)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vetaal API")

# Lets your frontend (running on a different port/origin while developing)
# make requests to this API. Lock this down to your real domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "vetaal-api"}


# ---------------------------------------------------------------
# Characters
# ---------------------------------------------------------------

@app.get("/api/characters", response_model=list[schemas.CharacterOut])
def list_characters(db: Session = Depends(get_db)):
    return db.query(models.Character).order_by(models.Character.sort_order).all()


# ---------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------

@app.get("/api/chapters", response_model=list[schemas.ChapterOut])
def list_chapters(db: Session = Depends(get_db)):
    return db.query(models.Chapter).order_by(models.Chapter.sort_order).all()


@app.get("/api/chapters/{chapter_id}", response_model=schemas.ChapterDetailOut)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


# ---------------------------------------------------------------
# Auth
# ---------------------------------------------------------------

@app.post("/api/auth/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.refresh(new_user)
    return new_user


@app.post("/api/auth/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------
# Reading progress (requires login)
# ---------------------------------------------------------------

@app.post("/api/progress/{chapter_id}", status_code=201)
def mark_chapter_read(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    existing = (
        db.query(models.ReadingProgress)
        .filter_by(user_id=current_user.id, chapter_id=chapter_id)
        .first()
    )
    if existing:
        return {"status": "already marked read"}

    entry = models.ReadingProgress(user_id=current_user.id, chapter_id=chapter_id)
    db.add(entry)
    db.commit()
    return {"status": "marked read"}


@app.get("/api/progress", response_model=list[schemas.ProgressOut])
def get_my_progress(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.ReadingProgress)
        .filter(models.ReadingProgress.user_id == current_user.id)
        .all()
    )


# ---------------------------------------------------------------
# Riddle quiz
# ---------------------------------------------------------------

@app.get("/api/chapters/{chapter_id}/riddle", response_model=schemas.RiddleOut)
def get_riddle_for_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """Public — anyone can read the question. Only login is required to submit an answer."""
    riddle = db.query(models.Riddle).filter(models.Riddle.chapter_id == chapter_id).first()
    if not riddle:
        raise HTTPException(status_code=404, detail="No riddle for this chapter yet")
    return riddle


@app.post("/api/riddles/{riddle_id}/answer", response_model=schemas.AnswerResult)
def submit_riddle_answer(
    riddle_id: int,
    payload: schemas.AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    riddle = db.query(models.Riddle).filter(models.Riddle.id == riddle_id).first()
    if not riddle:
        raise HTTPException(status_code=404, detail="Riddle not found")

    # simple case-insensitive, whitespace-trimmed comparison
    is_correct = payload.answer.strip().lower() == riddle.correct_answer.strip().lower()

    attempt = models.RiddleAttempt(
        user_id=current_user.id,
        riddle_id=riddle_id,
        submitted_answer=payload.answer,
        is_correct=is_correct,
    )
    db.add(attempt)
    db.commit()

    message = "The Vetaal nods. You may pass — for tonight." if is_correct else "Wrong. The Vetaal will ask again tomorrow."
    return {"is_correct": is_correct, "message": message}


@app.get("/api/riddles/attempts", response_model=list[schemas.AttemptOut])
def get_my_attempts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.RiddleAttempt)
        .filter(models.RiddleAttempt.user_id == current_user.id)
        .order_by(models.RiddleAttempt.attempted_at.desc())
        .all()
    )