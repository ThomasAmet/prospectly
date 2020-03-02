"""empty message

Revision ID: 68c430e1a4dc
Revises: a39cc9e878b4
Create Date: 2020-02-22 18:00:29.710592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68c430e1a4dc'
down_revision = 'a39cc9e878b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('next_payment', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscriptions', 'next_payment')
    # ### end Alembic commands ###
