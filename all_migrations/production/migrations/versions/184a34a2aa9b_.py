"""empty message

Revision ID: 184a34a2aa9b
Revises: 1bb060536ba5
Create Date: 2020-04-28 17:43:30.992329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '184a34a2aa9b'
down_revision = '1bb060536ba5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lead_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contact_lead_id', sa.Integer(), nullable=True),
    sa.Column('company_lead_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('contact_id', sa.Integer(), nullable=True),
    sa.Column('query_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
    sa.ForeignKeyConstraint(['company_lead_id'], ['company_leads.id'], ),
    sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
    sa.ForeignKeyConstraint(['contact_lead_id'], ['contact_leads.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lead_requests')
    # ### end Alembic commands ###
