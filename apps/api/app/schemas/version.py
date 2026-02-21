from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class VersionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    meeting_id: str
    version_num: int
    ai_output_json: dict
    rendered_markdown: str
    status: str
    redacted: bool
    created_at: datetime
    created_by: str


class VersionMarkdownUpdate(BaseModel):
    rendered_markdown: str
