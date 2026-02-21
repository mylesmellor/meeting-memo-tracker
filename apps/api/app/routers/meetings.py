import uuid
from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, and_, or_
from slowapi import Limiter

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.models.meeting import Meeting, MeetingCategory, MeetingStatus
from app.models.meeting_version import MeetingVersion, VersionStatus
from app.models.action_item import ActionItem, ActionStatus, ActionPriority
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingTranscriptPaste, MeetingOut, MeetingListOut
from app.schemas.version import VersionOut, VersionMarkdownUpdate
from app.services.ai_service import ai_service
from app.services.file_service import file_service

router = APIRouter(prefix="/meetings", tags=["meetings"])
limiter = Limiter(key_func=lambda r: str(getattr(getattr(r, "state", None), "user", None) and getattr(r.state.user, "id", None)) or r.client.host)


def meeting_to_out(m: Meeting, action_count: int = 0, latest_version_num: Optional[int] = None) -> dict:
    return {
        "id": str(m.id),
        "title": m.title,
        "category": m.category.value if hasattr(m.category, "value") else m.category,
        "tags": m.tags or [],
        "team_id": str(m.team_id) if m.team_id else None,
        "org_id": str(m.org_id),
        "owner_id": str(m.owner_id),
        "status": m.status.value if hasattr(m.status, "value") else m.status,
        "transcript_text": m.transcript_text,
        "file_path": m.file_path,
        "created_at": m.created_at,
        "updated_at": m.updated_at,
        "action_count": action_count,
        "latest_version_num": latest_version_num,
    }


@router.get("/")
async def list_meetings(
    request: Request,
    category: Optional[str] = None,
    team_id: Optional[str] = None,
    tags: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [Meeting.org_id == current_user.org_id]

    if category:
        filters.append(Meeting.category == category)
    if team_id:
        filters.append(Meeting.team_id == team_id)
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            filters.append(Meeting.tags.overlap(tag_list))
    if status:
        filters.append(Meeting.status == status)
    if date_from:
        filters.append(Meeting.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        filters.append(Meeting.created_at <= datetime.combine(date_to, datetime.max.time()))
    if q:
        filters.append(Meeting.search_vector.op("@@")(func.plainto_tsquery("english", q)))

    count_q = select(func.count(Meeting.id)).where(and_(*filters))
    total = (await db.execute(count_q)).scalar()

    meetings_q = (
        select(Meeting)
        .where(and_(*filters))
        .order_by(Meeting.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(meetings_q)
    meetings = result.scalars().all()

    items = []
    for m in meetings:
        action_count_r = await db.execute(
            select(func.count(ActionItem.id)).where(ActionItem.meeting_id == m.id)
        )
        action_count = action_count_r.scalar() or 0

        version_r = await db.execute(
            select(MeetingVersion.version_num)
            .where(MeetingVersion.meeting_id == m.id)
            .order_by(MeetingVersion.version_num.desc())
            .limit(1)
        )
        latest = version_r.scalar_one_or_none()
        items.append(meeting_to_out(m, action_count, latest))

    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/")
async def create_meeting(
    body: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meeting = Meeting(
        id=uuid.uuid4(),
        title=body.title,
        category=body.category,
        tags=body.tags,
        team_id=uuid.UUID(body.team_id) if body.team_id else None,
        org_id=current_user.org_id,
        owner_id=current_user.id,
        status=MeetingStatus.draft,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(meeting)
    await db.commit()
    return meeting_to_out(meeting)


@router.get("/{meeting_id}")
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)

    action_count_r = await db.execute(
        select(func.count(ActionItem.id)).where(ActionItem.meeting_id == m.id)
    )
    action_count = action_count_r.scalar() or 0

    version_r = await db.execute(
        select(MeetingVersion)
        .where(MeetingVersion.meeting_id == m.id)
        .order_by(MeetingVersion.version_num.desc())
        .limit(1)
    )
    latest_version = version_r.scalar_one_or_none()
    latest_num = latest_version.version_num if latest_version else None

    out = meeting_to_out(m, action_count, latest_num)
    if latest_version:
        out["latest_version"] = {
            "id": str(latest_version.id),
            "version_num": latest_version.version_num,
            "rendered_markdown": latest_version.rendered_markdown,
            "ai_output_json": latest_version.ai_output_json,
            "status": latest_version.status.value if hasattr(latest_version.status, "value") else latest_version.status,
            "redacted": latest_version.redacted,
            "created_at": latest_version.created_at.isoformat(),
        }
    return out


@router.patch("/{meeting_id}")
async def update_meeting(
    meeting_id: str,
    body: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    if body.title is not None:
        m.title = body.title
    if body.category is not None:
        m.category = body.category
    if body.tags is not None:
        m.tags = body.tags
    if body.team_id is not None:
        m.team_id = uuid.UUID(body.team_id)
    if body.status is not None:
        m.status = body.status
    m.updated_at = datetime.utcnow()
    await db.commit()
    return meeting_to_out(m)


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    await db.delete(m)
    await db.commit()


@router.post("/{meeting_id}/transcript")
async def set_transcript(
    meeting_id: str,
    body: MeetingTranscriptPaste,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    if len(body.text) > settings.MAX_TRANSCRIPT_CHARS:
        raise HTTPException(status_code=400, detail=f"Transcript exceeds {settings.MAX_TRANSCRIPT_CHARS} characters")
    m.transcript_text = body.text
    m.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Transcript saved"}


@router.post("/{meeting_id}/transcript/upload")
async def upload_transcript(
    meeting_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large")

    path = file_service.save(content, file.filename, str(current_user.org_id), str(m.id))
    text = file_service.extract_text(path)

    if len(text) > settings.MAX_TRANSCRIPT_CHARS:
        raise HTTPException(status_code=400, detail=f"Extracted text exceeds {settings.MAX_TRANSCRIPT_CHARS} characters")

    m.transcript_text = text
    m.file_path = path
    m.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "File uploaded and text extracted", "path": path}


@router.post("/{meeting_id}/generate")
async def generate_summary(
    request: Request,
    meeting_id: str,
    redact: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Store user on request state for rate limiter key
    request.state.user = current_user

    m = await _get_meeting_or_404(meeting_id, current_user, db)
    if not m.transcript_text:
        raise HTTPException(status_code=400, detail="No transcript available")

    # Generate AI output
    ai_json, markdown = await ai_service.generate(m.transcript_text, redact=redact)

    # Determine next version number
    version_count_r = await db.execute(
        select(func.count(MeetingVersion.id)).where(MeetingVersion.meeting_id == m.id)
    )
    version_num = (version_count_r.scalar() or 0) + 1

    version = MeetingVersion(
        id=uuid.uuid4(),
        meeting_id=m.id,
        version_num=version_num,
        ai_output_json=ai_json,
        rendered_markdown=markdown,
        status=VersionStatus.draft,
        redacted=redact,
        created_at=datetime.utcnow(),
        created_by=current_user.id,
    )
    db.add(version)
    await db.flush()

    # Bulk insert action items
    actions = ai_json.get("actions", [])
    for action in actions:
        due_date = None
        if action.get("due_date"):
            try:
                from datetime import date as date_type
                due_date = date_type.fromisoformat(action["due_date"])
            except (ValueError, TypeError):
                pass

        priority_val = action.get("priority", "medium")
        if priority_val not in ("low", "medium", "high"):
            priority_val = "medium"

        item = ActionItem(
            id=uuid.uuid4(),
            meeting_id=m.id,
            version_id=version.id,
            description=action.get("description", ""),
            owner_text=action.get("owner_text"),
            due_date=due_date,
            status=ActionStatus.todo,
            priority=ActionPriority(priority_val),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(item)

    # Update meeting title if AI suggests one and meeting has no custom title
    title_suggestion = ai_json.get("title_suggestion")
    if title_suggestion and m.title == "Untitled Meeting":
        m.title = title_suggestion

    m.updated_at = datetime.utcnow()
    await db.commit()

    # Update search_vector to include markdown content
    await db.execute(
        text("""
            UPDATE meetings
            SET search_vector = setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
                                setweight(to_tsvector('english', coalesce(:markdown,'')), 'B')
            WHERE id = :meeting_id
        """),
        {"markdown": markdown[:50000], "meeting_id": str(m.id)},
    )
    await db.commit()

    return {
        "id": str(version.id),
        "version_num": version.version_num,
        "rendered_markdown": version.rendered_markdown,
        "ai_output_json": version.ai_output_json,
        "status": version.status.value,
    }


@router.get("/{meeting_id}/versions")
async def list_versions(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    result = await db.execute(
        select(MeetingVersion)
        .where(MeetingVersion.meeting_id == m.id)
        .order_by(MeetingVersion.version_num.desc())
    )
    versions = result.scalars().all()
    return [
        {
            "id": str(v.id),
            "version_num": v.version_num,
            "status": v.status.value if hasattr(v.status, "value") else v.status,
            "redacted": v.redacted,
            "created_at": v.created_at.isoformat(),
        }
        for v in versions
    ]


@router.get("/{meeting_id}/versions/{version_num}")
async def get_version(
    meeting_id: str,
    version_num: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    result = await db.execute(
        select(MeetingVersion)
        .where(MeetingVersion.meeting_id == m.id, MeetingVersion.version_num == version_num)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return {
        "id": str(version.id),
        "meeting_id": str(version.meeting_id),
        "version_num": version.version_num,
        "ai_output_json": version.ai_output_json,
        "rendered_markdown": version.rendered_markdown,
        "status": version.status.value if hasattr(version.status, "value") else version.status,
        "redacted": version.redacted,
        "created_at": version.created_at.isoformat(),
        "created_by": str(version.created_by),
    }


@router.post("/{meeting_id}/versions/{version_num}/approve")
async def approve_version(
    meeting_id: str,
    version_num: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    result = await db.execute(
        select(MeetingVersion)
        .where(MeetingVersion.meeting_id == m.id, MeetingVersion.version_num == version_num)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    version.status = VersionStatus.approved
    m.status = MeetingStatus.approved
    m.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Version approved"}


@router.put("/{meeting_id}/versions/{version_num}")
async def edit_version_markdown(
    meeting_id: str,
    version_num: int,
    body: VersionMarkdownUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = await _get_meeting_or_404(meeting_id, current_user, db)
    result = await db.execute(
        select(MeetingVersion)
        .where(MeetingVersion.meeting_id == m.id, MeetingVersion.version_num == version_num)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    version.rendered_markdown = body.rendered_markdown
    await db.commit()
    return {"message": "Markdown updated"}


async def _get_meeting_or_404(meeting_id: str, current_user: User, db: AsyncSession) -> Meeting:
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.org_id == current_user.org_id)
    )
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return m
