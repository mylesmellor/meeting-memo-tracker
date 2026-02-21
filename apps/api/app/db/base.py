# Import all models here so Alembic autogenerate can detect them
from app.db.base_class import Base  # noqa: F401
from app.models.organisation import Organisation  # noqa: F401
from app.models.team import Team  # noqa: F401
from app.models.user import User, UserTeam  # noqa: F401
from app.models.meeting import Meeting  # noqa: F401
from app.models.meeting_version import MeetingVersion  # noqa: F401
from app.models.action_item import ActionItem  # noqa: F401
