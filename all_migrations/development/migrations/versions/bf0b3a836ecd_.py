"""empty message

Revision ID: bf0b3a836ecd
Revises: 2d8b402af198
Create Date: 2020-01-27 22:08:50.747853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf0b3a836ecd'
down_revision = '2d8b402af198'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('done', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'done')
    # ### end Alembic commands ###