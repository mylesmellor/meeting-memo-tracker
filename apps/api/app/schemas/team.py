from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str


class TeamUpdate(BaseModel):
    name: Optional[str] = None


class TeamOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    org_id: str
    name: str
    slug: str
    created_at: datetime
