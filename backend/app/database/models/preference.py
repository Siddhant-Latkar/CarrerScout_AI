from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, ForeignKey, String, Text, text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User


class Preference(TimestampMixin, Base):
    """Profile details and job search preferences for one user."""

    __tablename__ = "preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )

    degree: Mapped[str | None] = mapped_column(String(100))
    branch: Mapped[str | None] = mapped_column(String(100))
    graduation_year: Mapped[int | None]

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        server_default=text("'{}'"),
    )
    preferred_locations: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        server_default=text("'{}'"),
    )
    job_types: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        server_default=text("'{}'"),
    )

    paid_only: Mapped[bool] = mapped_column(default=True, server_default=true())
    min_monthly_stipend: Mapped[int | None]  # in rupees per month

    user: Mapped["User"] = relationship(back_populates="preference")
