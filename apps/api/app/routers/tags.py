from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.models.meeting import Meeting
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])

PRESETS = {
    "work": ["strategy", "kickoff", "planning", "review", "retrospective", "product", "sales", "finance", "operations", "hr"],
    "home": ["family", "logistics", "planning", "health", "finances", "school", "travel"],
    "private": ["personal", "goals", "journal", "health", "finance"],
}


@router.get("/recent")
async def recent_tags(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        select(func.unnest(Meeting.tags).label("tag"), func.max(Meeting.created_at).label("last_used"))
        .where(Meeting.org_id == current_user.org_id)
    )
    if category:
        q = q.where(Meeting.category == category)
    q = q.group_by("tag").order_by(func.max(Meeting.created_at).desc()).limit(20)

    result = await db.execute(q)
    rows = result.all()
    return [row.tag for row in rows]


@router.get("/presets")
async def preset_tags(category: Optional[str] = None):
    if category and category in PRESETS:
        return PRESETS[category]
    # Return all presets flat
    all_tags = []
    seen = set()
    for tags in PRESETS.values():
        for t in tags:
            if t not in seen:
                all_tags.append(t)
                seen.add(t)
    return all_tags
