from typing import Optional
from pydantic import BaseModel


class AIAction(BaseModel):
    description: str
    owner_text: Optional[str] = None
    due_date: Optional[str] = None  # YYYY-MM-DD
    priority: str = "medium"


class AIFollowupEmail(BaseModel):
    subject: str
    body_bullets: list[str]


class AIOutput(BaseModel):
    title_suggestion: str
    management_summary: list[str]
    decisions: list[str]
    actions: list[AIAction]
    risks_issues: list[str]
    next_agenda: list[str]
    followup_email: Optional[AIFollowupEmail] = None
