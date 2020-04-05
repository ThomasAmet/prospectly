"""Adding stripe_session_id to User attributes

Revision ID: 9fe8c2aade66
Revises: 27ba5d85a15d
Create Date: 2020-02-14 09:47:32.914037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fe8c2aade66'
down_revision = '27ba5d85a15d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('stripe_session_id', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'stripe_session_id')
    # ### end Alembic commands ###