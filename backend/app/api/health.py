from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db

router = APIRouter(tags=["health"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple status so we know the API is running."""
    return {"status": "ok"}


@router.get("/health/db")
def health_check_db(db: DbSession) -> dict[str, str]:
    """Run a trivial query to prove the database connection works."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok"}
