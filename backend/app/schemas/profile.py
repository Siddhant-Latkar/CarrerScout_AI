from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.database.models import Preference, User
from app.schemas.user import FullName

JobType = Literal["internship", "full_time", "part_time"]

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
SkillItem = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
LocationItem = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


def _remove_duplicates(values: list[str]) -> list[str]:
    """Drop repeated items ignoring case and preserve original order."""
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        key = value.casefold()

        if key not in seen:
            seen.add(key)
            result.append(value)

    return result


class ProfileUpdate(BaseModel):
    """Input schema for replacing a user's complete profile."""

    full_name: FullName
    degree: ShortText | None = None
    branch: ShortText | None = None
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    skills: list[SkillItem] = Field(default_factory=list, max_length=50)
    preferred_locations: list[LocationItem] = Field(default_factory=list, max_length=20)
    job_types: list[JobType] = Field(default_factory=list, max_length=10)
    paid_only: bool = True
    min_monthly_stipend: int | None = Field(default=None, ge=0, le=10_000_000)

    @field_validator("degree", "branch")
    @classmethod
    def blank_text_becomes_none(cls, value: str | None) -> str | None:
        return value or None

    @field_validator("skills", "preferred_locations", "job_types")
    @classmethod
    def remove_duplicate_items(cls, values: list[str]) -> list[str]:
        return _remove_duplicates(values)


class ProfileRead(BaseModel):
    """Output schema containing account details and job preferences."""

    email: str
    full_name: str
    degree: str | None
    branch: str | None
    graduation_year: int | None
    skills: list[str]
    preferred_locations: list[str]
    job_types: list[str]
    paid_only: bool
    min_monthly_stipend: int | None
    updated_at: datetime

    @classmethod
    def from_models(cls, user: User, preference: Preference) -> Self:
        return cls(
            email=user.email,
            full_name=user.full_name,
            degree=preference.degree,
            branch=preference.branch,
            graduation_year=preference.graduation_year,
            skills=preference.skills,
            preferred_locations=preference.preferred_locations,
            job_types=preference.job_types,
            paid_only=preference.paid_only,
            min_monthly_stipend=preference.min_monthly_stipend,
            updated_at=preference.updated_at,
        )
