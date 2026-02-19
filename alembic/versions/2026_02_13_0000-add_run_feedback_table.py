"""add run_feedback table

Revision ID: add_run_feedback_table
Revises: 43217e31df12
Create Date: 2026-02-13 00:00:00.000000+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_run_feedback_table"
down_revision: Union[str, None] = "43217e31df12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "run_feedback",
        sa.Column("feedback_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("workflow_run_id", sa.String(), nullable=True),
        sa.Column("task_id", sa.String(), nullable=True),
        sa.Column("feedback_value", sa.Integer(), nullable=False),
        sa.Column("categories", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("comment", sa.UnicodeText(), nullable=True),
        sa.Column("created_by_user_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.organization_id"],
        ),
        sa.PrimaryKeyConstraint("feedback_id"),
    )
    op.create_index(
        op.f("ix_run_feedback_workflow_run_id"),
        "run_feedback",
        ["workflow_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_run_feedback_task_id"),
        "run_feedback",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_run_feedback_organization_id"),
        "run_feedback",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "idx_run_feedback_org_created",
        "run_feedback",
        ["organization_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_run_feedback_org_created", table_name="run_feedback")
    op.drop_index(op.f("ix_run_feedback_organization_id"), table_name="run_feedback")
    op.drop_index(op.f("ix_run_feedback_task_id"), table_name="run_feedback")
    op.drop_index(op.f("ix_run_feedback_workflow_run_id"), table_name="run_feedback")
    op.drop_table("run_feedback")
