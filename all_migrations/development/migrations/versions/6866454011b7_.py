"""empty message

Revision ID: 6866454011b7
Revises: c6d9712b7a46
Create Date: 2020-04-08 20:18:49.958653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6866454011b7'
down_revision = 'c6d9712b7a46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('opportunity_steps', sa.Column('stage_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'opportunity_steps', 'commercial_stages', ['stage_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'opportunity_steps', type_='foreignkey')
    op.drop_column('opportunity_steps', 'stage_id')
    # ### end Alembic commands ###
