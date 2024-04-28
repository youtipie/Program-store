"""Increase password field max size

Revision ID: 42e921757cd1
Revises: f1249a3d9f44
Create Date: 2024-04-28 11:52:03.178870

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42e921757cd1'
down_revision = 'f1249a3d9f44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=256),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)

    # ### end Alembic commands ###