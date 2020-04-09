"""empty message

Revision ID: 3ca155956390
Revises: b95bf9009b6d
Create Date: 2020-03-28 02:40:47.123344

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3ca155956390'
down_revision = 'b95bf9009b6d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lead_requests')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lead_requests',
    sa.Column('query_date', mysql.DATETIME(), nullable=True),
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###