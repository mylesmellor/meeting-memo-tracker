"""Initial schema with all tables and search vector trigger

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organisations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("org_admin", "team_admin", "member", name="userrole"), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "user_teams",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "meetings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("category", sa.Enum("work", "home", "private", name="meetingcategory"), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="SET NULL"), nullable=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.Enum("draft", "approved", name="meetingstatus"), nullable=False, server_default="draft"),
        sa.Column("transcript_text", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR(), server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "meeting_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_num", sa.Integer(), nullable=False),
        sa.Column("ai_output_json", postgresql.JSONB(), nullable=False),
        sa.Column("rendered_markdown", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("draft", "approved", name="versionstatus"), nullable=False, server_default="draft"),
        sa.Column("redacted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )

    op.create_table(
        "action_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("meeting_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("owner_text", sa.String(255), nullable=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Enum("todo", "doing", "done", "blocked", name="actionstatus"), nullable=False, server_default="todo"),
        sa.Column("priority", sa.Enum("low", "medium", "high", name="actionpriority"), nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Full-text search trigger on meetings
    op.execute("""
        CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector := setweight(to_tsvector('english', coalesce(NEW.title,'')), 'A');
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER meetings_search_vector_update
          BEFORE INSERT OR UPDATE ON meetings
          FOR EACH ROW EXECUTE FUNCTION update_search_vector();
    """)

    op.execute("""
        CREATE INDEX meetings_search_idx ON meetings USING GIN(search_vector);
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS meetings_search_vector_update ON meetings")
    op.execute("DROP FUNCTION IF EXISTS update_search_vector")
    op.execute("DROP INDEX IF EXISTS meetings_search_idx")
    op.drop_table("action_items")
    op.drop_table("meeting_versions")
    op.drop_table("meetings")
    op.drop_table("user_teams")
    op.drop_table("users")
    op.drop_table("teams")
    op.drop_table("organisations")
    op.execute("DROP TYPE IF EXISTS actionpriority")
    op.execute("DROP TYPE IF EXISTS actionstatus")
    op.execute("DROP TYPE IF EXISTS versionstatus")
    op.execute("DROP TYPE IF EXISTS meetingstatus")
    op.execute("DROP TYPE IF EXISTS meetingcategory")
    op.execute("DROP TYPE IF EXISTS userrole")
