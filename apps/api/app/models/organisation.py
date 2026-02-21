import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base


class Organisation(Base):
    __tablename__ = "organisations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    teams: Mapped[list["Team"]] = relationship("Team", back_populates="organisation", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship("User", back_populates="organisation", cascade="all, delete-orphan")
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="organisation", cascade="all, delete-orphan")
