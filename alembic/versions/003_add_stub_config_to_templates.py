"""Add stub_config to templates

Revision ID: 003_add_stub_config_to_templates
Revises: 247c9eaeb1ce, c975d20ddc1d
Create Date: 2026-02-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_stub_config_to_templates'
down_revision: Union[str, Sequence[str], None] = ('247c9eaeb1ce', 'c975d20ddc1d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('templates', sa.Column('stub_config', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('templates', 'stub_config')