import re
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_role
from app.models.team import Team
from app.models.user import User, UserTeam, UserRole
from app.schemas.team import TeamCreate, TeamUpdate, TeamOut

router = APIRouter(prefix="/teams", tags=["teams"])


def slugify(name: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug[:80]


@router.get("/")
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Team).where(Team.org_id == current_user.org_id).order_by(Team.name)
    )
    teams = result.scalars().all()
    return [TeamOut.model_validate(t) for t in teams]


@router.post("/")
async def create_team(
    body: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.org_admin, UserRole.team_admin)),
):
    team = Team(
        id=uuid.uuid4(),
        org_id=current_user.org_id,
        name=body.name,
        slug=slugify(body.name),
        created_at=datetime.utcnow(),
    )
    db.add(team)
    await db.commit()
    return TeamOut.model_validate(team)


@router.get("/{team_id}")
async def get_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = await _get_team_or_404(team_id, current_user, db)
    return TeamOut.model_validate(team)


@router.patch("/{team_id}")
async def update_team(
    team_id: str,
    body: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = await _get_team_or_404(team_id, current_user, db)
    if body.name:
        team.name = body.name
        team.slug = slugify(body.name)
    await db.commit()
    return TeamOut.model_validate(team)


@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.org_admin)),
):
    team = await _get_team_or_404(team_id, current_user, db)
    await db.delete(team)
    await db.commit()


@router.get("/{team_id}/members")
async def list_members(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = await _get_team_or_404(team_id, current_user, db)
    result = await db.execute(
        select(User).join(UserTeam, User.id == UserTeam.user_id).where(UserTeam.team_id == team.id)
    )
    users = result.scalars().all()
    return [{"id": str(u.id), "name": u.name, "email": u.email, "role": u.role.value} for u in users]


@router.post("/{team_id}/members/{user_id}")
async def add_member(
    team_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.org_admin, UserRole.team_admin)),
):
    team = await _get_team_or_404(team_id, current_user, db)
    # Check user belongs to same org
    user_r = await db.execute(
        select(User).where(User.id == user_id, User.org_id == current_user.org_id)
    )
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await db.execute(
        select(UserTeam).where(UserTeam.user_id == uuid.UUID(user_id), UserTeam.team_id == team.id)
    )
    if not existing.scalar_one_or_none():
        db.add(UserTeam(user_id=uuid.UUID(user_id), team_id=team.id))
        await db.commit()
    return {"message": "Member added"}


@router.delete("/{team_id}/members/{user_id}", status_code=204)
async def remove_member(
    team_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.org_admin, UserRole.team_admin)),
):
    team = await _get_team_or_404(team_id, current_user, db)
    result = await db.execute(
        select(UserTeam).where(UserTeam.user_id == uuid.UUID(user_id), UserTeam.team_id == team.id)
    )
    membership = result.scalar_one_or_none()
    if membership:
        await db.delete(membership)
        await db.commit()


async def _get_team_or_404(team_id: str, current_user: User, db: AsyncSession) -> Team:
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.org_id == current_user.org_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
