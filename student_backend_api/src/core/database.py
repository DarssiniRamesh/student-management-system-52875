"""
Database configuration and connection management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings
from ..models.base import Base

# Ensure settings.database_url exists and is string
db_url = getattr(settings, "database_url", None)
if not db_url:
    raise RuntimeError("DATABASE_URL is not set or settings misconfigured. Please check your .env file.")

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all database tables.
    
    This function creates all tables defined in the models.
    Should be called during application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data in the database.
    Should only be used in development or testing.
    """
    Base.metadata.drop_all(bind=engine)
