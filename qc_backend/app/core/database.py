"""
Database Configuration — SQLAlchemy + SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file stored in /data folder
DATABASE_URL = "sqlite:///./data/quickcommerce.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ── Dependency: get DB session ─────────────────────────────────────────────────
def get_db():
    """Yield a database session, then close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
