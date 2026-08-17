"""
Pydantic models define what JSON goes IN and OUT of the API.
This is separate from models.py (the database tables) on purpose:
you often don't want to expose every DB column to the outside world
(e.g. never send hashed_password back in a response).

FastAPI uses these to auto-validate requests and auto-generate the
/docs page.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ---------- Character ----------

class CharacterOut(BaseModel):
    id: int
    code: str
    name: str
    name_devanagari: Optional[str] = None
    role: Optional[str] = None
    description: str

    class Config:
        from_attributes = True  # lets this read directly from a SQLAlchemy object


# ---------- Chapter ----------

class ChapterOut(BaseModel):
    id: int
    number: int
    riddle_label: str
    title: str
    access_tier: str

    class Config:
        from_attributes = True


class ChapterDetailOut(ChapterOut):
    content: Optional[str] = None


# ---------- Auth / User ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Reading progress ----------

class ProgressOut(BaseModel):
    chapter_id: int
    read_at: datetime

    class Config:
        from_attributes = True


# ---------- Riddle quiz ----------

class RiddleOut(BaseModel):
    """Sent to the frontend. Notice: no correct_answer field here —
    never send the answer to the client, or anyone could read it
    from the browser's Network tab and cheat."""
    id: int
    chapter_id: int
    question: str
    hint: Optional[str] = None

    class Config:
        from_attributes = True


class AnswerSubmit(BaseModel):
    answer: str


class AnswerResult(BaseModel):
    is_correct: bool
    message: str


class AttemptOut(BaseModel):
    riddle_id: int
    submitted_answer: str
    is_correct: bool
    attempted_at: datetime

    class Config:
        from_attributes = True