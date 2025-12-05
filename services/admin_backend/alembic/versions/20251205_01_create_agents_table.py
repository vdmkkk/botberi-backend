"""create agents table

Revision ID: 20251205_01_agents
Revises:
Create Date: 2025-12-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20251205_01_agents"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("activation_code", sa.String(length=64), nullable=False),
        sa.Column("rate", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("activation_code", name="uq_agents_activation_code"),
    )


def downgrade() -> None:
    op.drop_table("agents")


