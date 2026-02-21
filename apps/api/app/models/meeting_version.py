import uuid
import enum
from datetime import datetime
from sqlalchemy import Text, ForeignKey, Enum, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base_class import Base


class VersionStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"


class MeetingVersion(Base):
    __tablename__ = "meeting_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    version_num: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_output_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    rendered_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[VersionStatus] = mapped_column(Enum(VersionStatus), default=VersionStatus.draft, nullable=False)
    redacted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="versions")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    action_items: Mapped[list["ActionItem"]] = relationship("ActionItem", back_populates="version")
