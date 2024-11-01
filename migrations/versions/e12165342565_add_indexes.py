"""Add indexes

Revision ID: e12165342565
Revises: 42e921757cd1
Create Date: 2024-05-05 12:29:20.360349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e12165342565'
down_revision = '42e921757cd1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comment_date'), ['date'], unique=False)

    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_game_popularity'), ['popularity'], unique=False)
        batch_op.create_index(batch_op.f('ix_game_rating'), ['rating'], unique=False)
        batch_op.create_index(batch_op.f('ix_game_title'), ['title'], unique=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('user_email_key', type_='unique')
        batch_op.drop_constraint('user_username_key', type_='unique')
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_email'))
        batch_op.create_unique_constraint('user_username_key', ['username'])
        batch_op.create_unique_constraint('user_email_key', ['email'])

    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_game_title'))
        batch_op.drop_index(batch_op.f('ix_game_rating'))
        batch_op.drop_index(batch_op.f('ix_game_popularity'))

    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comment_date'))

    # ### end Alembic commands ###
