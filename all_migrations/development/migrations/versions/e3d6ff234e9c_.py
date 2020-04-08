"""empty message

Revision ID: e3d6ff234e9c
Revises: 9f82c4bf68fe
Create Date: 2020-03-24 14:55:52.005911

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e3d6ff234e9c'
down_revision = '9f82c4bf68fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('commercial_stages', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_constraint('lead_requests_ibfk_1', 'lead_requests', type_='foreignkey')
    op.create_foreign_key(None, 'lead_requests', 'company_leads', ['company_lead_id'], ['id'])
    op.create_foreign_key(None, 'lead_requests', 'contacts_leads', ['contact_lead_id'], ['id'])
    op.drop_column('lead_requests', 'lead_id')
    op.add_column('leads', sa.Column('contact_firstname', sa.String(length=60), nullable=True))
    op.add_column('leads', sa.Column('contact_lastname', sa.String(length=60), nullable=True))
    op.add_column('leads', sa.Column('contact_position', sa.String(length=60), nullable=True))
    op.create_index(op.f('ix_leads_company_activity_field'), 'leads', ['company_activity_field'], unique=False)
    op.create_index(op.f('ix_leads_contact_firstname'), 'leads', ['contact_firstname'], unique=False)
    op.create_index(op.f('ix_leads_contact_lastname'), 'leads', ['contact_lastname'], unique=False)
    op.create_index(op.f('ix_leads_contact_position'), 'leads', ['contact_position'], unique=False)
    op.drop_column('leads', 'owner_firstname')
    op.drop_column('leads', 'company_email_bcc')
    op.drop_column('leads', 'owner_lastname')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('leads', sa.Column('owner_lastname', mysql.VARCHAR(length=60), nullable=True))
    op.add_column('leads', sa.Column('company_email_bcc', mysql.VARCHAR(length=120), nullable=True))
    op.add_column('leads', sa.Column('owner_firstname', mysql.VARCHAR(length=60), nullable=True))
    op.drop_index(op.f('ix_leads_contact_position'), table_name='leads')
    op.drop_index(op.f('ix_leads_contact_lastname'), table_name='leads')
    op.drop_index(op.f('ix_leads_contact_firstname'), table_name='leads')
    op.drop_index(op.f('ix_leads_company_activity_field'), table_name='leads')
    op.drop_column('leads', 'contact_position')
    op.drop_column('leads', 'contact_lastname')
    op.drop_column('leads', 'contact_firstname')
    op.add_column('lead_requests', sa.Column('lead_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'lead_requests', type_='foreignkey')
    op.drop_constraint(None, 'lead_requests', type_='foreignkey')
    op.create_foreign_key('lead_requests_ibfk_1', 'lead_requests', 'leads', ['lead_id'], ['id'])
    op.alter_column('commercial_stages', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    # ### end Alembic commands ###
