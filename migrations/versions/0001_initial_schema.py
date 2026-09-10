"""Create the initial content and contact-message tables.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    table_names = sa.inspect(op.get_bind()).get_table_names()

    # Existing local databases were created before Alembic was introduced.
    # Checking first lets them adopt this baseline without losing their data.
    if "site_content" not in table_names:
        op.create_table(
            "site_content",
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("data", sa.JSON(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("key"),
        )

    if "contact_messages" not in table_names:
        op.create_table(
            "contact_messages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("phone", sa.String(length=32), nullable=True),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_contact_messages_email", "contact_messages", ["email"], unique=False)


def downgrade() -> None:
    table_names = sa.inspect(op.get_bind()).get_table_names()
    if "contact_messages" in table_names:
        op.drop_table("contact_messages")
    if "site_content" in table_names:
        op.drop_table("site_content")
