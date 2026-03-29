from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.entry import ResumeData


class OAuthProvider(BaseModel):
    provider: str
    provider_id: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    oauth_providers: list[OAuthProvider] = []
    has_resume_profile: bool = False
    created_at: datetime
    updated_at: datetime


class ResumeProfileResponse(BaseModel):
    resume_profile: ResumeData


class UserInDB(BaseModel):
    email: str
    password_hash: str | None = None
    name: str
    oauth_providers: list[OAuthProvider] = []
    resume_profile: ResumeData = ResumeData()
    created_at: datetime
    updated_at: datetime
