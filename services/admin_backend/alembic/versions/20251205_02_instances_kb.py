"""create instances and knowledge base tables

Revision ID: 20251205_02_instances
Revises: 20251205_01_agents
Create Date: 2025-12-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20251205_02_instances"
down_revision: str | None = "20251205_01_agents"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

instance_status_enum = sa.Enum(
    "pending",
    "provisioning",
    "running",
    "failed",
    "stopped",
    name="instance_status",
)
kb_entry_status_enum = sa.Enum(
    "queued",
    "processing",
    "ready",
    "failed",
    name="kb_entry_status",
)
kb_data_type_enum = sa.Enum("document", "video", "other", name="kb_data_type")
kb_lang_hint_enum = sa.Enum("en", "es", "other", name="kb_lang_hint")
LISTEN_CHANNEL = "instances_notify"


def upgrade() -> None:
    bind = op.get_bind()
    instance_status_enum.create(bind, checkfirst=True)
    kb_entry_status_enum.create(bind, checkfirst=True)
    kb_data_type_enum.create(bind, checkfirst=True)
    kb_lang_hint_enum.create(bind, checkfirst=True)

    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION notify_domain_event() RETURNS trigger AS $$
        DECLARE
            row_data jsonb;
            payload jsonb;
        BEGIN
            IF (TG_OP = 'DELETE') THEN
                row_data := row_to_json(OLD)::jsonb;
            ELSE
                row_data := row_to_json(NEW)::jsonb;
            END IF;

            payload := jsonb_build_object(
                'routing_key', TG_ARGV[0],
                'table', TG_TABLE_NAME,
                'op', TG_OP,
                'schema_version', 1,
                'data', row_data
            );

            PERFORM pg_notify('{LISTEN_CHANNEL}', payload::text);

            IF (TG_OP = 'DELETE') THEN
                RETURN OLD;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.create_table(
        "instances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bot_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "user_config",
            sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "pipeline_config",
            sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
           	server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("status", instance_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "knowledge_bases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "instance_id",
            sa.Integer(),
            sa.ForeignKey("instances.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "knowledge_base_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "knowledge_base_id",
            sa.Integer(),
            sa.ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("data_type", kb_data_type_enum, nullable=True),
        sa.Column("lang_hint", kb_lang_hint_enum, nullable=True),
        sa.Column("status", kb_entry_status_enum, nullable=False, server_default="queued"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Triggers for instances
    op.execute(
        """
        CREATE TRIGGER trg_instances_insert
        AFTER INSERT ON instances
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('instance.created');
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_instances_update
        AFTER UPDATE ON instances
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('instance.updated');
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_instances_delete
        AFTER DELETE ON instances
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('instance.deleted');
        """
    )

    # Knowledge base triggers
    op.execute(
        """
        CREATE TRIGGER trg_kb_insert
        AFTER INSERT ON knowledge_bases
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('knowledge_base.created');
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_kb_delete
        AFTER DELETE ON knowledge_bases
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('knowledge_base.deleted');
        """
    )

    # Knowledge base entry triggers
    op.execute(
        """
        CREATE TRIGGER trg_kb_entry_insert
        AFTER INSERT ON knowledge_base_entries
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('knowledge_base.entry.created');
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_kb_entry_update
        AFTER UPDATE ON knowledge_base_entries
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('knowledge_base.entry.updated');
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_kb_entry_delete
        AFTER DELETE ON knowledge_base_entries
        FOR EACH ROW EXECUTE FUNCTION notify_domain_event('knowledge_base.entry.deleted');
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_kb_entry_delete ON knowledge_base_entries;")
    op.execute("DROP TRIGGER IF EXISTS trg_kb_entry_update ON knowledge_base_entries;")
    op.execute("DROP TRIGGER IF EXISTS trg_kb_entry_insert ON knowledge_base_entries;")
    op.execute("DROP TRIGGER IF EXISTS trg_kb_delete ON knowledge_bases;")
    op.execute("DROP TRIGGER IF EXISTS trg_kb_insert ON knowledge_bases;")
    op.execute("DROP TRIGGER IF EXISTS trg_instances_delete ON instances;")
    op.execute("DROP TRIGGER IF EXISTS trg_instances_update ON instances;")
    op.execute("DROP TRIGGER IF EXISTS trg_instances_insert ON instances;")

    op.drop_table("knowledge_base_entries")
    op.drop_table("knowledge_bases")
    op.drop_table("instances")

    op.execute("DROP FUNCTION IF EXISTS notify_domain_event;")

    bind = op.get_bind()
    kb_lang_hint_enum.drop(bind, checkfirst=True)
    kb_data_type_enum.drop(bind, checkfirst=True)
    kb_entry_status_enum.drop(bind, checkfirst=True)
    instance_status_enum.drop(bind, checkfirst=True)


