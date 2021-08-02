"""add BP columns

Revision ID: 2bf09f1ac47f
Revises: 7a8f7c05822c
Create Date: 2021-08-02 14:41:02.141830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bf09f1ac47f'
down_revision = '7a8f7c05822c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('notifications', sa.Column('eventId', sa.VARCHAR(length=25)))
    op.add_column('notifications', sa.Column('status', sa.VARCHAR(length=25)))
    op.add_column('notifications', sa.Column('eventType', sa.VARCHAR(length=100)))
    op.add_column('notifications', sa.Column('amount', sa.VARCHAR(length=25)))
    pass


def downgrade():
    op.drop_column('notifications', 'eventId')
    op.drop_column('notifications', 'status')
    op.drop_column('notifications', 'eventType')
    op.drop_column('notifications', 'amount')
    pass
