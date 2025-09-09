from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    content: str = Field(..., description="The message content")
    sender: str = Field(default="user", description="The sender of the message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Message timestamp")

class ChatResponse(BaseModel):
    content: str = Field(..., description="The response content")
    sender: str = Field(default="assistant", description="The response sender")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Response timestamp")

class ChatHistory(BaseModel):
    messages: list[ChatMessage] = Field(default=[], description="List of chat messages")
