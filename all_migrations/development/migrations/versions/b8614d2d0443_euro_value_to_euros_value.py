"""euro_value to euros_value

Revision ID: b8614d2d0443
Revises: bc88dead23ba
Create Date: 2020-01-28 17:12:58.339167

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b8614d2d0443'
down_revision = 'bc88dead23ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('opportunities', sa.Column('euros_value', sa.Numeric(precision=6, scale=2), nullable=True))
    op.drop_column('opportunities', 'euro_value')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('opportunities', sa.Column('euro_value', mysql.DECIMAL(precision=6, scale=2), nullable=True))
    op.drop_column('opportunities', 'euros_value')
    # ### end Alembic commands ###
