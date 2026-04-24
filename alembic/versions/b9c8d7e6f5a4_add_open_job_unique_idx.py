"""add open generation job unique index

Revision ID: b9c8d7e6f5a4
Revises: 12a18f870c9f, r4s5t6u7v8w9
Create Date: 2026-04-24 23:40:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b9c8d7e6f5a4"
down_revision = ("12a18f870c9f", "r4s5t6u7v8w9")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_cgj_open_user_section_topic_grade",
        "content_generation_jobs",
        ["requested_by_user_id", "job_type", "topic", "grade_band"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('pending', 'running', 'awaiting_human_approval', 'publishing')"
        ),
    )


def downgrade() -> None:
    op.drop_index("uq_cgj_open_user_section_topic_grade", table_name="content_generation_jobs")
