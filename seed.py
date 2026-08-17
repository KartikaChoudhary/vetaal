"""
Run this once after your tables exist to fill the database with
the same characters/chapters that are currently hardcoded in the HTML.

    python seed.py

Safe to re-run: it skips rows that already exist.
"""

from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

characters = [
    dict(code="HEIR · UNCROWNED", name="Prince Aran", name_devanagari="युवराज अरण",
         role="Crown Prince", sort_order=1,
         description="He hasn't slept a full night since the pyre. The Vetaal won't allow it "
                      "— and he's starting to suspect it doesn't want him crowned until he "
                      "knows the truth."),
    dict(code="SPIRIT · RIDER OF CORPSES", name="The Vetaal", name_devanagari="वेताल",
         role="Spirit", sort_order=2,
         description="It has worn twelve dead courtiers this month alone. Its riddles are "
                      "never really about the dead man it's borrowing — they're about the prince."),
    dict(code="REGENT · WIDOW QUEEN", name="Rajmata Indira", name_devanagari="राजमाता इंदिरा",
         role="Regent", sort_order=3,
         description="She raised a king. She's no longer certain she raised someone who can "
                      "survive one week of this. She has her own reasons to fear the riddles."),
    dict(code="COURT ASTROLOGER", name="Bhanu", name_devanagari="ज्योतिषी भानु",
         role="Astrologer", sort_order=4,
         description="He read the stars the night the old king died. He hasn't spoken a full "
                      "sentence since — but he keeps writing the same warning, over and over."),
]

chapters = [
    dict(number=1, riddle_label="Riddle I", title="The Empty Throne", access_tier="free", sort_order=1),
    dict(number=2, riddle_label="Riddle II", title="What the Ash Remembers", access_tier="free", sort_order=2),
    dict(number=3, riddle_label="Riddle III", title="The Regent's Price", access_tier="fast_pass", sort_order=3),
    dict(number=4, riddle_label="Riddle IV", title="A Question of Blood", access_tier="fast_pass", sort_order=4),
    dict(number=5, riddle_label="Riddle V", title="The Last Coronation", access_tier="new", sort_order=5),
]

for c in characters:
    exists = db.query(models.Character).filter_by(name=c["name"]).first()
    if not exists:
        db.add(models.Character(**c))

for ch in chapters:
    exists = db.query(models.Chapter).filter_by(number=ch["number"]).first()
    if not exists:
        db.add(models.Chapter(**ch))

db.commit()  # commit chapters first so their IDs exist for the riddles below

# Map chapter number -> the chapter's row, so we can attach riddles by chapter_id
chapter_by_number = {c.number: c for c in db.query(models.Chapter).all()}

riddles = [
    dict(chapter_number=1,
         question="I am taken before I am given. What am I?",
         correct_answer="an oath",
         hint="Think of what a new king swears before the crown ever touches his head."),
    dict(chapter_number=2,
         question="What remembers everything but repeats nothing?",
         correct_answer="ash",
         hint="It is what a pyre leaves behind."),
    dict(chapter_number=3,
         question="What is given freely but never without a price?",
         correct_answer="loyalty",
         hint="A regent's greatest currency."),
]

for r in riddles:
    chapter = chapter_by_number.get(r["chapter_number"])
    if not chapter:
        continue
    exists = db.query(models.Riddle).filter_by(chapter_id=chapter.id).first()
    if not exists:
        db.add(models.Riddle(
            chapter_id=chapter.id,
            question=r["question"],
            correct_answer=r["correct_answer"],
            hint=r["hint"],
        ))

db.commit()
print("Seed complete.")
db.close()