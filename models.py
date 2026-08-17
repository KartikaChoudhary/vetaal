"""
These classes ARE the database tables. SQLAlchemy reads them and
knows how to create matching Postgres tables (see seed.py / main.py
where Base.metadata.create_all(engine) is called).

Each class = one table. Each attribute = one column.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # lets you do user.progress to get all their reading progress rows
    progress = relationship("ReadingProgress", back_populates="user")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False)          # e.g. "HEIR · UNCROWNED"
    name = Column(String, nullable=False)           # e.g. "Prince Aran"
    name_devanagari = Column(String, nullable=True)  # e.g. "युवराज अरण"
    role = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False, unique=True)   # 1, 2, 3...
    riddle_label = Column(String, nullable=False)             # "Riddle I"
    title = Column(String, nullable=False)                    # "The Empty Throne"
    content = Column(Text, nullable=True)                     # the actual chapter text
    access_tier = Column(String, default="free")              # "free" | "fast_pass" | "new"
    sort_order = Column(Integer, default=0)

    progress = relationship("ReadingProgress", back_populates="chapter")


class ReadingProgress(Base):
    """One row per (user, chapter) they've read."""
    __tablename__ = "reading_progress"
    __table_args__ = (UniqueConstraint("user_id", "chapter_id", name="uix_user_chapter"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="progress")
    chapter = relationship("Chapter", back_populates="progress")


class Riddle(Base):
    """The Vetaal's question for a given chapter. One chapter can have one riddle."""
    __tablename__ = "riddles"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    question = Column(Text, nullable=False)
    # Stored lowercase/trimmed for simple case-insensitive matching.
    correct_answer = Column(String, nullable=False)
    hint = Column(String, nullable=True)

    attempts = relationship("RiddleAttempt", back_populates="riddle")


class RiddleAttempt(Base):
    """Every time a user submits an answer, one row is stored here — right or wrong."""
    __tablename__ = "riddle_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    riddle_id = Column(Integer, ForeignKey("riddles.id"), nullable=False)
    submitted_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    riddle = relationship("Riddle", back_populates="attempts")