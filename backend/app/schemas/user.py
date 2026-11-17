from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)

# Emails are stored in lowercase.
Email = Annotated[EmailStr, AfterValidator(str.lower)]

FullName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]

NewPassword = Annotated[
    str,
    StringConstraints(min_length=8, max_length=128),
]


class UserCreate(BaseModel):
    email: Email
    password: NewPassword
    full_name: FullName


class LoginRequest(BaseModel):
    email: Email
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
