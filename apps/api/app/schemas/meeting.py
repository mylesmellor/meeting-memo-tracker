import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, model_validator
from app.models.meeting import MeetingCategory, MeetingStatus


class MeetingCreate(BaseModel):
    title: str
    category: MeetingCategory
    tags: list[str] = []
    team_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_work_team(self):
        if self.category == MeetingCategory.work and not self.team_id:
            raise ValueError("team_id is required for work meetings")
        return self


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[MeetingCategory] = None
    tags: Optional[list[str]] = None
    team_id: Optional[str] = None
    status: Optional[MeetingStatus] = None


class MeetingTranscriptPaste(BaseModel):
    text: str


class MeetingOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    title: str
    category: str
    tags: list[str]
    team_id: Optional[str]
    org_id: str
    owner_id: str
    status: str
    transcript_text: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    action_count: int = 0
    latest_version_num: Optional[int] = None


class MeetingListOut(BaseModel):
    items: list[MeetingOut]
    total: int
    skip: int
    limit: int
