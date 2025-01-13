"""add a comment_id coloumn

Revision ID: 749479b48467
Revises: da980e90516c
Create Date: 2025-01-13 06:47:38.280746

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '749479b48467'
down_revision = 'da980e90516c'
branch_labels = None
depends_on = None

def upgrade():
    # Add `comment_id` column with nullable=True and create a foreign key
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_notification_comment', 'comment', ['comment_id'], ['id'])  # Explicit FK name

def downgrade():
    # Drop the foreign key and column during downgrade
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_constraint('fk_notification_comment', type_='foreignkey')  # Explicit FK name
        batch_op.drop_column('comment_id')

