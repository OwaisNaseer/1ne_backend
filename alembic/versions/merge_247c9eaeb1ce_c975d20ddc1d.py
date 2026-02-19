"""Merge chatbot and profile picture heads

Revision ID: merge_247c9eaeb1ce_c975d20ddc1d
Revises: 247c9eaeb1ce, c975d20ddc1d
Create Date: 2026-02-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "merge_247c9eaeb1ce_c975d20ddc1d"
down_revision: Union[str, Sequence[str], None] = ("247c9eaeb1ce", "c975d20ddc1d")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op merge migration to join branches."""
    pass


def downgrade() -> None:
    """No-op downgrade for merge migration."""
    pass

