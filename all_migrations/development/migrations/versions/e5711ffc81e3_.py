"""empty message

Revision ID: e5711ffc81e3
Revises: 58c06d0bef24
Create Date: 2020-03-16 00:18:19.775369

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e5711ffc81e3'
down_revision = '58c06d0bef24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('status', sa.Column('name', sa.String(length=30), nullable=True))
    op.drop_index('title', table_name='status')
    op.create_unique_constraint(None, 'status', ['name'])
    op.drop_column('status', 'title')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('status', sa.Column('title', mysql.VARCHAR(length=30), nullable=True))
    op.drop_constraint(None, 'status', type_='unique')
    op.create_index('title', 'status', ['title'], unique=True)
    op.drop_column('status', 'name')
    # ### end Alembic commands ###
