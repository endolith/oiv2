from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Response(BaseModel):
    content: str = Field(description="The content of the message")
    summary: str = Field(description="A summary of the message")

class Message(BaseModel):
    role: MessageRole
    response: Response
    content: str

class StreamToken(BaseModel):
    content: str
    done: bool = False
    error: Optional[str] = None 