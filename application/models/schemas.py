from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    query: str
    answer: str


class HealthResponse(BaseModel):
    status: str


class ReviewRequest(BaseModel):
    code: str
    language: Optional[str] = None
    mode: Optional[str] = "full"  # full | security | performance | explain
