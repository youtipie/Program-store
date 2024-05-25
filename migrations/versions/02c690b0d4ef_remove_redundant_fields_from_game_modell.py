"""Remove redundant fields from Game modell

Revision ID: 02c690b0d4ef
Revises: 21dd28d9b822
Create Date: 2024-05-24 20:22:19.000886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02c690b0d4ef'
down_revision = '21dd28d9b822'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_index('ix_game_rating')
        batch_op.drop_column('rating')
        batch_op.drop_column('rating_count')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating_count', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('rating', sa.DOUBLE_PRECISION(precision=53), server_default=sa.text("'0'::double precision"), autoincrement=False, nullable=True))
        batch_op.create_index('ix_game_rating', ['rating'], unique=False)

    # ### end Alembic commands ###