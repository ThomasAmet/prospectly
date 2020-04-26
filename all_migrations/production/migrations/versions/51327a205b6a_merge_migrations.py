"""merge migrations

Revision ID: 51327a205b6a
Revises: 2258e53ad53e, eb0cc42bca99
Create Date: 2020-04-26 05:22:19.342425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51327a205b6a'
down_revision = ('2258e53ad53e', 'eb0cc42bca99')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
