"""empty message

Revision ID: 06b5dbdc7150
Revises: a1bf24fdcc5f
Create Date: 2020-04-28 05:56:38.841406

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '06b5dbdc7150'
down_revision = 'a1bf24fdcc5f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('subscriptions', sa.Column('cancellation_date', sa.DateTime(), nullable=True))
  
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
  
    op.drop_column('subscriptions', 'cancellation_date')
    
    # ### end Alembic commands ###