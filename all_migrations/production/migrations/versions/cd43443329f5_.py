"""empty message

Revision ID: cd43443329f5
Revises: 3e37f4921bb8
Create Date: 2020-03-23 04:04:43.245600

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cd43443329f5'
down_revision = '3e37f4921bb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('company_id', sa.Integer(), nullable=True))
    op.drop_constraint('notes_ibfk_2', 'notes', type_='foreignkey')
    op.create_foreign_key(None, 'notes', 'companies', ['company_id'], ['id'])
    op.drop_column('notes', 'comapny_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('comapny_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'notes', type_='foreignkey')
    op.create_foreign_key('notes_ibfk_2', 'notes', 'companies', ['comapny_id'], ['id'])
    op.drop_column('notes', 'company_id')
    # ### end Alembic commands ###