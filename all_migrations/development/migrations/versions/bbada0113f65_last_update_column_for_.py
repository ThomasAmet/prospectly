"""last_update column for CommercialStageStep

Revision ID: bbada0113f65
Revises: b8614d2d0443
Create Date: 2020-01-28 18:45:14.434950

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bbada0113f65'
down_revision = 'b8614d2d0443'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('commercial_stage_steps', sa.Column('last_update', sa.DateTime(), nullable=True))
    op.drop_column('notes', 'last_update')
    op.drop_column('tasks', 'last_update')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('last_update', mysql.DATETIME(), nullable=True))
    op.add_column('notes', sa.Column('last_update', mysql.DATETIME(), nullable=True))
    op.drop_column('commercial_stage_steps', 'last_update')
    # ### end Alembic commands ###
