"""empty message

Revision ID: e6d93536e848
Revises: bfdd87919101
Create Date: 2020-04-28 00:24:53.068843

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e6d93536e848'
down_revision = 'bfdd87919101'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.alter_column('companies', 'facebook',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('companies', 'instagram',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('companies', 'linkedin',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('company_leads', 'email',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=60),
               existing_nullable=True)
    op.alter_column('company_leads', 'facebook',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('company_leads', 'instagram',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('company_leads', 'linkedin',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('company_leads', 'website',
               existing_type=sa.VARCHAR(length=60),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('contact_leads', 'facebook',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('contact_leads', 'firstname',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=60),
               existing_nullable=False)
    op.alter_column('contact_leads', 'instagram',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('contact_leads', 'lastname',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=60),
               existing_nullable=False)
    op.alter_column('contact_leads', 'linkedin',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('contact_leads', 'position',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=60),
               existing_nullable=True)
    op.alter_column('contacts', 'facebook',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('contacts', 'instagram',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('contacts', 'linkedin',
               existing_type=sa.VARCHAR(length=120),
               type_=sa.String(length=240),
               existing_nullable=True)
    op.alter_column('notes', 'content',
               existing_type=sa.VARCHAR(length=240),
               type_=sa.String(length=2000),
               existing_nullable=True)
     # op.alter_column('contacts_emails', 'is_main',
     #           existing_type=mysql.TINYINT(display_width=1),
     #           type_=sa.Boolean(),
     #           existing_nullable=True)
    # op.alter_column('opportunities', 'deal_closed',
    #            existing_type=mysql.TINYINT(display_width=1),
    #            type_=sa.Boolean(),
    #            existing_nullable=True)
    # op.alter_column('commercial_stages', 'private',
    #            existing_type=mysql.TINYINT(display_width=1),
    #            type_=sa.Boolean(),
    #            existing_nullable=True)
    # op.alter_column('opportunities', 'euros_value',
    #            existing_type=mysql.DECIMAL(precision=6, scale=2),
    #            type_=sa.Numeric(precision=8, scale=2),
    #            existing_nullable=True)
    # op.alter_column('plans', 'lead_generator',
    #            existing_type=mysql.TINYINT(display_width=1),
    #            type_=sa.Boolean(),
    #            existing_nullable=True)
    # op.alter_column('plans', 'yearly',
    #            existing_type=mysql.TINYINT(display_width=1),
    #            type_=sa.Boolean(),
    #            existing_nullable=True)
    # op.alter_column('tasks', 'done',
    #            existing_type=mysql.TINYINT(display_width=1),
    #            type_=sa.Boolean(),
    #            existing_nullable=True)
    # op.alter_column('users', 'admin',
    #            existing_type=mysql.TINYINT(display_width=1),
    #            type_=sa.Boolean(),
    #            existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.alter_column('users', 'admin',
    #            existing_type=sa.Boolean(),
    #            type_=mysql.TINYINT(display_width=1),
    #            existing_nullable=True)
    # op.alter_column('tasks', 'done',
    #            existing_type=sa.Boolean(),
    #            type_=mysql.TINYINT(display_width=1),
    #            existing_nullable=True)
    # op.alter_column('plans', 'yearly',
    #            existing_type=sa.Boolean(),
    #            type_=mysql.TINYINT(display_width=1),
    #            existing_nullable=True)
    # op.alter_column('plans', 'lead_generator',
    #            existing_type=sa.Boolean(),
    #            type_=mysql.TINYINT(display_width=1),
    #            existing_nullable=True)
    # op.alter_column('opportunities', 'euros_value',
    #            existing_type=sa.Numeric(precision=8, scale=2),
    #            type_=mysql.DECIMAL(precision=6, scale=2),
    #            existing_nullable=True)
    # op.alter_column('opportunities', 'deal_closed',
    #            existing_type=sa.Boolean(),
    #            type_=mysql.TINYINT(display_width=1),
    #            existing_nullable=True)
    op.alter_column('notes', 'content',
               existing_type=sa.String(length=2000),
               type_=sa.VARCHAR(length=240),
               existing_nullable=True)
    op.alter_column('contacts_emails', 'is_main',
               existing_type=sa.Boolean(),
               type_=sa.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('contacts', 'linkedin',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('contacts', 'instagram',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('contacts', 'facebook',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('contact_leads', 'position',
               existing_type=sa.String(length=60),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('contact_leads', 'linkedin',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('contact_leads', 'lastname',
               existing_type=sa.String(length=60),
               type_=sa.VARCHAR(length=120),
               existing_nullable=False)
    op.alter_column('contact_leads', 'instagram',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('contact_leads', 'firstname',
               existing_type=sa.String(length=60),
               type_=sa.VARCHAR(length=120),
               existing_nullable=False)
    op.alter_column('contact_leads', 'facebook',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('company_leads', 'website',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=60),
               existing_nullable=True)
    op.alter_column('company_leads', 'linkedin',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('company_leads', 'instagram',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('company_leads', 'facebook',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('company_leads', 'email',
               existing_type=sa.String(length=60),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('companies', 'linkedin',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('companies', 'instagram',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    op.alter_column('companies', 'facebook',
               existing_type=sa.String(length=240),
               type_=sa.VARCHAR(length=120),
               existing_nullable=True)
    # op.alter_column('commercial_stages', 'private',
    #            existing_type=sa.Boolean(),
    #            type_=mysql.TINYINT(display_width=1),
    #            existing_nullable=True)
    # ### end Alembic commands ###
