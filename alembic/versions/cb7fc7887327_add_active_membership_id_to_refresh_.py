"""add_active_membership_id_to_refresh_tokens

Revision ID: cb7fc7887327
Revises: d6e42d4a8046
Create Date: 2026-01-05 02:15:24.158645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb7fc7887327'
down_revision: Union[str, None] = 'd6e42d4a8046'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add active_membership_id column to refresh_tokens table
    op.add_column('refresh_tokens', 
        sa.Column('active_membership_id', sa.UUID(), nullable=True)
    )
    op.create_index(op.f('ix_refresh_tokens_active_membership_id'), 'refresh_tokens', ['active_membership_id'], unique=False)
    op.create_foreign_key(
        'fk_refresh_tokens_active_membership_id',
        'refresh_tokens', 'user_memberships',
        ['active_membership_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Remove active_membership_id column from refresh_tokens table
    op.drop_constraint('fk_refresh_tokens_active_membership_id', 'refresh_tokens', type_='foreignkey')
    op.drop_index(op.f('ix_refresh_tokens_active_membership_id'), table_name='refresh_tokens')
    op.drop_column('refresh_tokens', 'active_membership_id')

