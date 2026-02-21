from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.models.action_item import ActionStatus, ActionPriority


class ActionItemCreate(BaseModel):
    meeting_id: str
    description: str
    owner_text: Optional[str] = None
    due_date: Optional[date] = None
    status: ActionStatus = ActionStatus.todo
    priority: ActionPriority = ActionPriority.medium


class ActionItemUpdate(BaseModel):
    description: Optional[str] = None
    owner_text: Optional[str] = None
    owner_user_id: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[ActionStatus] = None
    priority: Optional[ActionPriority] = None


class ActionItemOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    meeting_id: str
    version_id: Optional[str] = None
    description: str
    owner_text: Optional[str] = None
    owner_user_id: Optional[str] = None
    due_date: Optional[date] = None
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    meeting_title: Optional[str] = None
    meeting_category: Optional[str] = None


class ActionItemListOut(BaseModel):
    items: list[ActionItemOut]
    total: int
    skip: int
    limit: int
