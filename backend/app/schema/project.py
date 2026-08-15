from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


import uuid

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    repository_url: Optional[str] = None
    default_branch: Optional[str] = None
    github_token: Optional[str] = None
    llm_model: Optional[str] = None
    system_prompt: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    archived: Optional[bool] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    owner_id: Optional[uuid.UUID] = None
    name: str
    slug: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    default_branch: Optional[str] = None
    github_token: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    llm_model: Optional[str] = None
    system_prompt: Optional[str] = None
    archived: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectStatsResponse(BaseModel):
    linesChanged: int
    filesModified: int
    testsPassed: int
    totalCommits: int
    activeAgents: int
    timeSaved: str