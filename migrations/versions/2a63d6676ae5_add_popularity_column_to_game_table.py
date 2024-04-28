"""Add popularity column to game table

Revision ID: 2a63d6676ae5
Revises: 96134eeb6539
Create Date: 2024-03-10 08:46:48.996783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2a63d6676ae5'
down_revision: Union[str, None] = '96134eeb6539'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('game', sa.Column('popularity', sa.Integer(), server_default='0'))


def downgrade():
    op.drop_column('game', 'popularity')
