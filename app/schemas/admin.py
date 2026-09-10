from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.content import HomepageContent

MessageStatus = Literal["unread", "read", "archived"]


class HomepageContentResponse(BaseModel):
    data: HomepageContent
    updated_at: datetime


class HomepageContentUpdate(BaseModel):
    data: HomepageContent


class ContactMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str | None
    message: str
    status: MessageStatus
    read_at: datetime | None
    created_at: datetime


class ContactMessageStatusUpdate(BaseModel):
    status: MessageStatus
