"""Pydantic v2 contracts for auth. Mirrors specs/api/auth.md."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SignupRequest(StrictModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(StrictModel):
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=1, max_length=72)


class AuthUserResponse(BaseModel):
    user_id: UUID
    email: str
