from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    TBD = "TBD"


class Status(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[Status] = None

    class Config:
        extra = "forbid"


class TicketRead(BaseModel):
    id: UUID
    title: str
    description: str
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
