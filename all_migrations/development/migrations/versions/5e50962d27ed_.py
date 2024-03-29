"""empty message

Revision ID: 5e50962d27ed
Revises: 3ca155956390
Create Date: 2020-03-28 02:44:54.569506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e50962d27ed'
down_revision = '3ca155956390'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lead_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contact_lead_id', sa.Integer(), nullable=True),
    sa.Column('company_lead_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('query_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_lead_id'], ['company_leads.id'], ),
    sa.ForeignKeyConstraint(['contact_lead_id'], ['contact_leads.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lead_requests')
    # ### end Alembic commands ###
