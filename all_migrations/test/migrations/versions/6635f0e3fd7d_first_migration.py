"""first migration

Revision ID: 6635f0e3fd7d
Revises: 
Create Date: 2020-01-30 19:19:58.754769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6635f0e3fd7d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('company_name', sa.String(length=120), nullable=True),
    sa.Column('company_address', sa.String(length=120), nullable=True),
    sa.Column('company_postal_code', sa.String(length=30), nullable=True),
    sa.Column('company_city', sa.String(length=60), nullable=True),
    sa.Column('company_email', sa.String(length=120), nullable=True),
    sa.Column('company_email_bcc', sa.String(length=120), nullable=True),
    sa.Column('company_phone', sa.String(length=60), nullable=True),
    sa.Column('company_activity_field', sa.String(length=60), nullable=False),
    sa.Column('owner_firstname', sa.String(length=60), nullable=True),
    sa.Column('owner_lastname', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_company_activity_field'), 'leads', ['company_activity_field'], unique=False)
    op.create_index(op.f('ix_leads_owner_firstname'), 'leads', ['owner_firstname'], unique=False)
    op.create_index(op.f('ix_leads_owner_lastname'), 'leads', ['owner_lastname'], unique=False)
    op.create_table('notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('note_content', sa.String(length=240), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_name', sa.String(length=30), nullable=True),
    sa.Column('monthly_price', sa.Integer(), nullable=True),
    sa.Column('yearly_price', sa.Integer(), nullable=True),
    sa.Column('limit_daily_query', sa.Integer(), nullable=True),
    sa.Column('crm_access', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plans_plan_name'), 'plans', ['plan_name'], unique=False)
    op.create_table('status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=30), nullable=True),
    sa.Column('last_name', sa.String(length=30), nullable=True),
    sa.Column('username', sa.String(length=60), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=120), nullable=True),
    sa.Column('registration_date', sa.DateTime(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('commercial_stages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('closing_perc', sa.Numeric(precision=2, scale=2), nullable=True),
    sa.Column('private', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('company_name', sa.String(length=120), nullable=True),
    sa.Column('company_address', sa.String(length=120), nullable=True),
    sa.Column('company_postal_code', sa.String(length=30), nullable=True),
    sa.Column('company_city', sa.String(length=60), nullable=True),
    sa.Column('company_email', sa.String(length=120), nullable=True),
    sa.Column('company_email_bcc', sa.String(length=120), nullable=True),
    sa.Column('company_phone', sa.String(length=60), nullable=True),
    sa.Column('company_activity_field', sa.String(length=60), nullable=False),
    sa.Column('owner_firstname', sa.String(length=60), nullable=True),
    sa.Column('owner_lastname', sa.String(length=60), nullable=True),
    sa.Column('website', sa.String(length=120), nullable=True),
    sa.Column('facebook', sa.String(length=120), nullable=True),
    sa.Column('instagram', sa.String(length=120), nullable=True),
    sa.Column('linkedin', sa.String(length=120), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_company_activity_field'), 'contacts', ['company_activity_field'], unique=False)
    op.create_index(op.f('ix_contacts_owner_firstname'), 'contacts', ['owner_firstname'], unique=False)
    op.create_index(op.f('ix_contacts_owner_lastname'), 'contacts', ['owner_lastname'], unique=False)
    op.create_table('lead_requests',
    sa.Column('lead_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('query_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('lead_id', 'user_id')
    )
    op.create_table('subscriptions',
    sa.Column('plan_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('yearly', sa.Boolean(), nullable=True),
    sa.Column('subscription_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('plan_id', 'user_id')
    )
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('task_title', sa.String(length=60), nullable=True),
    sa.Column('task_content', sa.String(length=240), nullable=True),
    sa.Column('priority', sa.String(length=30), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('done', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('opportunities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('contact_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('euros_value', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('deal_closed', sa.Boolean(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('commercial_stage_steps',
    sa.Column('opportunity_id', sa.Integer(), nullable=False),
    sa.Column('commercial_stage_id', sa.Integer(), nullable=False),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.Column('note_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['commercial_stage_id'], ['commercial_stages.id'], ),
    sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['status.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.PrimaryKeyConstraint('opportunity_id', 'commercial_stage_id', 'status_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('commercial_stage_steps')
    op.drop_table('opportunities')
    op.drop_table('tasks')
    op.drop_table('subscriptions')
    op.drop_table('lead_requests')
    op.drop_index(op.f('ix_contacts_owner_lastname'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_owner_firstname'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_company_activity_field'), table_name='contacts')
    op.drop_table('contacts')
    op.drop_table('commercial_stages')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('status')
    op.drop_index(op.f('ix_plans_plan_name'), table_name='plans')
    op.drop_table('plans')
    op.drop_table('notes')
    op.drop_index(op.f('ix_leads_owner_lastname'), table_name='leads')
    op.drop_index(op.f('ix_leads_owner_firstname'), table_name='leads')
    op.drop_index(op.f('ix_leads_company_activity_field'), table_name='leads')
    op.drop_table('leads')
    # ### end Alembic commands ###
