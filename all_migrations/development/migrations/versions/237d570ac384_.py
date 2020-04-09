"""empty message

Revision ID: 237d570ac384
Revises: a0391b81c9b7
Create Date: 2020-03-28 02:01:40.344848

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '237d570ac384'
down_revision = 'a0391b81c9b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('lead_requests_ibfk_3', 'lead_requests', type_='foreignkey')
    op.drop_column('lead_requests', 'contact_lead_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead_requests', sa.Column('contact_lead_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('lead_requests_ibfk_3', 'lead_requests', 'contacts_leads', ['contact_lead_id'], ['id'])
    # ### end Alembic commands ###
