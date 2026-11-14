from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# The engine manages connections to PostgreSQL. It connects lazily, on first use.
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Give each request its own database session and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
