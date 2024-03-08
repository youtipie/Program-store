"""Add rating and rating_count columns to Game

Revision ID: 39651f5df930
Revises: 
Create Date: 2024-03-08 13:03:45.403583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '39651f5df930'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('game', sa.Column('rating', sa.Float(), nullable=False, server_default='0'))
    op.add_column('game', sa.Column('rating_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('game', 'rating')
    op.drop_column('game', 'rating_count')
