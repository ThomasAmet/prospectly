"""empty message

Revision ID: 995b8a4bdd7b
Revises: dd41ab8ba94a
Create Date: 2020-04-06 02:46:39.103958

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '995b8a4bdd7b'
down_revision = 'dd41ab8ba94a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plans', sa.Column('stripe_id', sa.String(length=120), nullable=True))
    op.add_column('plans', sa.Column('yearly', sa.Boolean(), nullable=True))
    op.drop_column('plans', 'yearly_price')
    op.drop_column('subscriptions', 'yearly')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('yearly', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('plans', sa.Column('yearly_price', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('plans', 'yearly')
    op.drop_column('plans', 'stripe_id')
    # ### end Alembic commands ###
