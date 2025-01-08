"""third migratiom

Revision ID: 581e41cc2db3
Revises: 77a1afc35494
Create Date: 2025-01-06 15:38:36.702717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '581e41cc2db3'
down_revision = '77a1afc35494'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('post_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'post', ['post_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('post_id')

    # ### end Alembic commands ###
