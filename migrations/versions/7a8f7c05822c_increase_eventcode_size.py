"""increase eventcode size

Revision ID: 7a8f7c05822c
Revises: 113a1f19592f
Create Date: 2021-03-10 11:50:31.780403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a8f7c05822c'
down_revision = '113a1f19592f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('notifications', 'eventCode', existing_type=sa.VARCHAR(length=25), type_=sa.VARCHAR(length=30))


def downgrade():
    pass
