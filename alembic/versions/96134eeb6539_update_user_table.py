"""Update User table

Revision ID: 96134eeb6539
Revises: 39651f5df930
Create Date: 2024-03-08 13:12:15.126087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '96134eeb6539'
down_revision: Union[str, None] = '39651f5df930'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user', sa.Column('nickname', sa.String(100), nullable=False, unique=True))
    op.add_column('user', sa.Column('is_subscribed', sa.Boolean, default=False))
    op.add_column('user', sa.Column('avatar_path', sa.String(150), unique=True))
    op.add_column('user', sa.Column('reg_date', sa.DateTime, unique=True))


def downgrade():
    op.drop_column('user', 'nickname')
    op.drop_column('user', 'is_subscribed')
    op.drop_column('user', 'avatar_path')
    op.drop_column('user', 'reg_date')
