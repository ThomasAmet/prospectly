"""empty message

Revision ID: dd8023accf0b
Revises: af0ebc101d01
Create Date: 2020-03-26 14:26:22.441468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd8023accf0b'
down_revision = 'af0ebc101d01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company_leads', sa.Column('company_name', sa.String(length=120), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company_leads', 'company_name')
    # ### end Alembic commands ###
