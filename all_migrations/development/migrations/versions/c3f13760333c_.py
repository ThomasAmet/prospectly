"""empty message

Revision ID: c3f13760333c
Revises: e3d6ff234e9c
Create Date: 2020-03-26 03:42:18.501321

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c3f13760333c'
down_revision = 'e3d6ff234e9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company_leads', sa.Column('company_activity_field1', sa.String(length=60), nullable=False))
    op.add_column('company_leads', sa.Column('company_activity_field2', sa.String(length=60), nullable=True))
    op.add_column('company_leads', sa.Column('company_activity_field3', sa.String(length=60), nullable=True))
    op.add_column('company_leads', sa.Column('company_website', sa.String(length=60), nullable=True))
    op.drop_column('company_leads', 'company_name')
    op.create_index(op.f('ix_company_leads_company_activity_field1'), 'company_leads', ['company_activity_field1'], unique=False)
    op.create_index(op.f('ix_company_leads_company_activity_field2'), 'company_leads', ['company_activity_field2'], unique=False)
    op.create_index(op.f('ix_company_leads_company_activity_field3'), 'company_leads', ['company_activity_field3'], unique=False)
    op.create_index(op.f('ix_company_leads_company_city'), 'company_leads', ['company_city'], unique=False)
    op.drop_index('ix_company_leads_company_activity_field', table_name='company_leads')
    op.drop_index('ix_company_leads_contact_firstname', table_name='company_leads')
    op.drop_index('ix_company_leads_contact_lastname', table_name='company_leads')
    op.drop_index('ix_company_leads_contact_position', table_name='company_leads')
    op.drop_column('company_leads', 'company_activity_field')
    op.add_column('contacts_leads', sa.Column('contact_activity_field1', sa.String(length=120), nullable=False))
    op.add_column('contacts_leads', sa.Column('contact_activity_field2', sa.String(length=120), nullable=True))
    op.add_column('contacts_leads', sa.Column('contact_activity_field3', sa.String(length=120), nullable=True))
    op.add_column('contacts_leads', sa.Column('contact_company', sa.String(length=120), nullable=False))
    op.add_column('contacts_leads', sa.Column('contact_email', sa.String(length=120), nullable=True))
    op.add_column('contacts_leads', sa.Column('contact_firstname', sa.String(length=120), nullable=False))
    op.add_column('contacts_leads', sa.Column('contact_lastname', sa.String(length=120), nullable=False))
    op.add_column('contacts_leads', sa.Column('contact_linkedin', sa.String(length=120), nullable=True))
    op.add_column('contacts_leads', sa.Column('contact_phone', sa.String(length=120), nullable=True))
    op.add_column('contacts_leads', sa.Column('contact_position', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_contacts_leads_contact_activity_field1'), 'contacts_leads', ['contact_activity_field1'], unique=False)
    op.create_index(op.f('ix_contacts_leads_contact_activity_field2'), 'contacts_leads', ['contact_activity_field2'], unique=False)
    op.create_index(op.f('ix_contacts_leads_contact_activity_field3'), 'contacts_leads', ['contact_activity_field3'], unique=False)
    op.drop_column('contacts_leads', 'name')
    op.drop_constraint('lead_requests_ibfk_1', 'lead_requests', type_='foreignkey')
    op.create_foreign_key(None, 'lead_requests', 'contacts_leads', ['contact_lead_id'], ['id'])
    op.create_foreign_key(None, 'lead_requests', 'company_leads', ['company_lead_id'], ['id'])
    op.drop_column('lead_requests', 'lead_id')
    op.add_column('leads', sa.Column('contact_firstname', sa.String(length=60), nullable=True))
    op.add_column('leads', sa.Column('contact_lastname', sa.String(length=60), nullable=True))
    op.add_column('leads', sa.Column('contact_position', sa.String(length=60), nullable=True))
    op.create_index(op.f('ix_leads_company_activity_field'), 'leads', ['company_activity_field'], unique=False)
    op.create_index(op.f('ix_leads_contact_firstname'), 'leads', ['contact_firstname'], unique=False)
    op.create_index(op.f('ix_leads_contact_lastname'), 'leads', ['contact_lastname'], unique=False)
    op.create_index(op.f('ix_leads_contact_position'), 'leads', ['contact_position'], unique=False)
    op.drop_column('leads', 'company_email_bcc')
    op.drop_column('leads', 'owner_lastname')
    op.drop_column('leads', 'owner_firstname')
    # ### end Alembic commands ###


# def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('leads', sa.Column('owner_firstname', mysql.VARCHAR(length=60), nullable=True))
    op.add_column('leads', sa.Column('owner_lastname', mysql.VARCHAR(length=60), nullable=True))
    op.add_column('leads', sa.Column('company_email_bcc', mysql.VARCHAR(length=120), nullable=True))
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
    op.add_column('contacts_leads', sa.Column('name', mysql.VARCHAR(length=120), nullable=False))
    op.drop_index(op.f('ix_contacts_leads_contact_activity_field3'), table_name='contacts_leads')
    op.drop_index(op.f('ix_contacts_leads_contact_activity_field2'), table_name='contacts_leads')
    op.drop_index(op.f('ix_contacts_leads_contact_activity_field1'), table_name='contacts_leads')
    op.drop_column('contacts_leads', 'contact_position')
    op.drop_column('contacts_leads', 'contact_phone')
    op.drop_column('contacts_leads', 'contact_linkedin')
    op.drop_column('contacts_leads', 'contact_lastname')
    op.drop_column('contacts_leads', 'contact_firstname')
    op.drop_column('contacts_leads', 'contact_email')
    op.drop_column('contacts_leads', 'contact_company')
    op.drop_column('contacts_leads', 'contact_activity_field3')
    op.drop_column('contacts_leads', 'contact_activity_field2')
    op.drop_column('contacts_leads', 'contact_activity_field1')
    op.add_column('company_leads', sa.Column('company_activity_field', mysql.VARCHAR(length=60), nullable=False))
    op.create_index('ix_company_leads_contact_position', 'company_leads', ['contact_position'], unique=False)
    op.create_index('ix_company_leads_contact_lastname', 'company_leads', ['contact_lastname'], unique=False)
    op.create_index('ix_company_leads_contact_firstname', 'company_leads', ['contact_firstname'], unique=False)
    op.create_index('ix_company_leads_company_activity_field', 'company_leads', ['company_activity_field'], unique=False)
    op.drop_index(op.f('ix_company_leads_company_city'), table_name='company_leads')
    op.drop_index(op.f('ix_company_leads_company_activity_field3'), table_name='company_leads')
    op.drop_index(op.f('ix_company_leads_company_activity_field2'), table_name='company_leads')
    op.drop_index(op.f('ix_company_leads_company_activity_field1'), table_name='company_leads')
    op.add('company_leads', 'company_name', mysql.VARCHAR(length=120),nullable=True)
    op.drop_column('company_leads', 'company_website')
    op.drop_column('company_leads', 'company_activity_field3')
    op.drop_column('company_leads', 'company_activity_field2')
    op.drop_column('company_leads', 'company_activity_field1')

    # ### end Alembic commands ###