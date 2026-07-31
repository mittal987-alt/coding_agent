import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    role: str
    content: str


class ChatCreate(BaseModel):
    title: str
    project_id: Optional[uuid.UUID] = None
    model_name: str = "gpt-4o"
    provider: str = "openai"
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    title: str
    model_name: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True
