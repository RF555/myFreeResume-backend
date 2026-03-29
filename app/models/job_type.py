from datetime import datetime

from pydantic import BaseModel, Field


class JobTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class JobTypeUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class JobTypeResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
