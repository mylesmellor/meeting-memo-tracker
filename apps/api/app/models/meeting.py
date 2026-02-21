import uuid
import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TSVECTOR
from app.db.base_class import Base


class MeetingCategory(str, enum.Enum):
    work = "work"
    home = "home"
    private = "private"


class MeetingStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[MeetingCategory] = mapped_column(Enum(MeetingCategory), nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[MeetingStatus] = mapped_column(Enum(MeetingStatus), default=MeetingStatus.draft, nullable=False)
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    search_vector: Mapped[str] = mapped_column(TSVECTOR, server_default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="meetings")
    team: Mapped["Team | None"] = relationship("Team", back_populates="meetings")
    owner: Mapped["User"] = relationship("User", back_populates="meetings", foreign_keys=[owner_id])
    versions: Mapped[list["MeetingVersion"]] = relationship("MeetingVersion", back_populates="meeting", cascade="all, delete-orphan", order_by="MeetingVersion.version_num")
    action_items: Mapped[list["ActionItem"]] = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
