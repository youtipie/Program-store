"""Delete unique constraint from apk_name and cache_name

Revision ID: a76345fdf793
Revises: 8dbcacd7e012
Create Date: 2024-05-28 13:28:32.351878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a76345fdf793'
down_revision = '8dbcacd7e012'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_constraint('game_apk_name_key', type_='unique')
        batch_op.drop_constraint('game_cache_name_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.create_unique_constraint('game_cache_name_key', ['cache_name'])
        batch_op.create_unique_constraint('game_apk_name_key', ['apk_name'])

    # ### end Alembic commands ###