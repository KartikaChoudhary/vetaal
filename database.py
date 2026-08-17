"""
Sets up the connection to Postgres and gives us a way to
open/close a database "session" per request.

Everything else in the app imports `engine`, `Base`, or `get_db`
from here instead of talking to the database directly.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # reads the .env file into environment variables

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and fill it in."
    )

# The engine is the actual connection pool to Postgres.
engine = create_engine(DATABASE_URL)

# Each request gets its own Session (a "conversation" with the DB).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our model classes (User, Chapter, ...) will inherit from this.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency. Opens a session, hands it to the route function,
    then closes it afterwards -- even if the route raised an error.
    Used in routes like: def get_chapters(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
