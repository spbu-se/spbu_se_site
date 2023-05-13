"""merging two heads

Revision ID: 33ca5df0bfc2
Revises: 975cdf37ae8e, c4e88555c985
Create Date: 2022-10-11 14:21:26.150716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33ca5df0bfc2'
down_revision = ('975cdf37ae8e', 'c4e88555c985')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
