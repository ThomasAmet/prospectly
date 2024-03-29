"""empty message

Revision ID: 19e5b6b954f0
Revises: 002287808f51
Create Date: 2020-04-07 20:48:48.391422

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '19e5b6b954f0'
down_revision = '002287808f51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('subscriptions_ibfk_3', 'subscriptions', type_='foreignkey')
    # op.drop_column('subscriptions', 'plan_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('subscriptions', sa.Column('plan_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.create_foreign_key('subscriptions_ibfk_3', 'subscriptions', 'plans', ['plan_id'], ['id'])
    # ### end Alembic commands ###
