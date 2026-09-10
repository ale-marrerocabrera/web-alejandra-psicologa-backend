"""Add workflow status to contact messages.

Revision ID: 0003_add_contact_message_status
Revises: 0002_add_admin_authentication
Create Date: 2026-09-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_add_contact_message_status"
down_revision = "0002_add_admin_authentication"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "contact_messages",
        sa.Column("status", sa.String(length=16), nullable=False, server_default="unread"),
    )
    op.add_column("contact_messages", sa.Column("read_at", sa.DateTime(), nullable=True))
    op.create_index("ix_contact_messages_status", "contact_messages", ["status"], unique=False)
    op.alter_column("contact_messages", "status", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_contact_messages_status", table_name="contact_messages")
    op.drop_column("contact_messages", "read_at")
    op.drop_column("contact_messages", "status")
