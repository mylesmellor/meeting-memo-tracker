import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, DateTime, ForeignKey, Enum, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class ActionStatus(str, enum.Enum):
    todo = "todo"
    doing = "doing"
    done = "done"
    blocked = "blocked"


class ActionPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ActionItem(Base):
    __tablename__ = "action_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("meeting_versions.id", ondelete="SET NULL"), nullable=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    owner_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ActionStatus] = mapped_column(Enum(ActionStatus), default=ActionStatus.todo, nullable=False)
    priority: Mapped[ActionPriority] = mapped_column(Enum(ActionPriority), default=ActionPriority.medium, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="action_items")
    version: Mapped["MeetingVersion | None"] = relationship("MeetingVersion", back_populates="action_items")
    owner_user: Mapped["User | None"] = relationship("User", back_populates="action_items", foreign_keys=[owner_user_id])
