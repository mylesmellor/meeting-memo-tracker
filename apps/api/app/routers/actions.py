import uuid
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.deps import get_db, get_current_user
from app.models.action_item import ActionItem, ActionStatus, ActionPriority
from app.models.meeting import Meeting
from app.models.user import User
from app.schemas.action_item import ActionItemCreate, ActionItemUpdate, ActionItemOut

router = APIRouter(prefix="/actions", tags=["actions"])


def action_to_out(a: ActionItem, meeting: Optional[Meeting] = None) -> dict:
    return {
        "id": str(a.id),
        "meeting_id": str(a.meeting_id),
        "version_id": str(a.version_id) if a.version_id else None,
        "description": a.description,
        "owner_text": a.owner_text,
        "owner_user_id": str(a.owner_user_id) if a.owner_user_id else None,
        "due_date": a.due_date,
        "status": a.status.value if hasattr(a.status, "value") else a.status,
        "priority": a.priority.value if hasattr(a.priority, "value") else a.priority,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
        "meeting_title": meeting.title if meeting else None,
        "meeting_category": (meeting.category.value if hasattr(meeting.category, "value") else meeting.category) if meeting else None,
    }


@router.get("/")
async def list_actions(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_this_week: bool = False,
    overdue: bool = False,
    owner_text: Optional[str] = None,
    meeting_id: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Join with meetings to filter by org
    filters = [Meeting.org_id == current_user.org_id]

    if status:
        filters.append(ActionItem.status == status)
    if priority:
        filters.append(ActionItem.priority == priority)
    if owner_text:
        filters.append(ActionItem.owner_text.ilike(f"%{owner_text}%"))
    if meeting_id:
        filters.append(ActionItem.meeting_id == meeting_id)
    if category:
        filters.append(Meeting.category == category)
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            filters.append(Meeting.tags.overlap(tag_list))

    today = date.today()
    if overdue:
        filters.append(ActionItem.due_date < today)
        filters.append(ActionItem.status != ActionStatus.done)
    if due_this_week:
        week_end = today + timedelta(days=7)
        filters.append(ActionItem.due_date >= today)
        filters.append(ActionItem.due_date <= week_end)

    count_q = (
        select(func.count(ActionItem.id))
        .join(Meeting, ActionItem.meeting_id == Meeting.id)
        .where(and_(*filters))
    )
    total = (await db.execute(count_q)).scalar()

    q = (
        select(ActionItem, Meeting)
        .join(Meeting, ActionItem.meeting_id == Meeting.id)
        .where(and_(*filters))
        .order_by(ActionItem.due_date.asc().nulls_last(), ActionItem.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(q)
    rows = result.all()

    items = [action_to_out(a, m) for a, m in rows]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/")
async def create_action(
    body: ActionItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify meeting belongs to org
    meeting_r = await db.execute(
        select(Meeting).where(Meeting.id == body.meeting_id, Meeting.org_id == current_user.org_id)
    )
    meeting = meeting_r.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    item = ActionItem(
        id=uuid.uuid4(),
        meeting_id=uuid.UUID(body.meeting_id),
        description=body.description,
        owner_text=body.owner_text,
        due_date=body.due_date,
        status=body.status,
        priority=body.priority,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(item)
    await db.commit()
    return action_to_out(item, meeting)


@router.get("/{action_id}")
async def get_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a, m = await _get_action_or_404(action_id, current_user, db)
    return action_to_out(a, m)


@router.patch("/{action_id}")
async def update_action(
    action_id: str,
    body: ActionItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a, m = await _get_action_or_404(action_id, current_user, db)
    if body.description is not None:
        a.description = body.description
    if body.owner_text is not None:
        a.owner_text = body.owner_text
    if body.owner_user_id is not None:
        a.owner_user_id = uuid.UUID(body.owner_user_id)
    if body.due_date is not None:
        a.due_date = body.due_date
    if body.status is not None:
        a.status = body.status
    if body.priority is not None:
        a.priority = body.priority
    a.updated_at = datetime.utcnow()
    await db.commit()
    return action_to_out(a, m)


@router.delete("/{action_id}", status_code=204)
async def delete_action(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a, _ = await _get_action_or_404(action_id, current_user, db)
    await db.delete(a)
    await db.commit()


async def _get_action_or_404(action_id: str, current_user: User, db: AsyncSession):
    result = await db.execute(
        select(ActionItem, Meeting)
        .join(Meeting, ActionItem.meeting_id == Meeting.id)
        .where(ActionItem.id == action_id, Meeting.org_id == current_user.org_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Action item not found")
    return row
