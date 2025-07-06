from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from app.core.models import Priority, Status


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[Status] = None

    # class Config:
    #     extra = "forbid"

    model_config = ConfigDict(extra="forbid")


class TicketRead(BaseModel):
    id: UUID
    title: str
    description: str
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime

    # class Config:
    #     orm_mode = True

    model_config = ConfigDict(from_attributes=True)
