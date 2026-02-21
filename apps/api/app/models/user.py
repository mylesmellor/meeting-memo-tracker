import uuid
import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class UserRole(str, enum.Enum):
    org_admin = "org_admin"
    team_admin = "team_admin"
    member = "member"


class UserTeam(Base):
    __tablename__ = "user_teams"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="team_memberships")
    team: Mapped["Team"] = relationship("Team", back_populates="members")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.member, nullable=False)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="users")
    team_memberships: Mapped[list["UserTeam"]] = relationship("UserTeam", back_populates="user", cascade="all, delete-orphan")
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="owner", foreign_keys="Meeting.owner_id")
    action_items: Mapped[list["ActionItem"]] = relationship("ActionItem", back_populates="owner_user", foreign_keys="ActionItem.owner_user_id")
