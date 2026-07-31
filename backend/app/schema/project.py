from pydantic import BaseModel
from datetime import datetime
from typing import Optional


import uuid

class ProjectCreate(BaseModel):
    name: str
    repository_url: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    owner_id: Optional[uuid.UUID] = None
    name: str
    slug: str
    repository_url: Optional[str] = None
    default_branch: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    archived: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
