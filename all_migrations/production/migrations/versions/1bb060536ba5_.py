"""empty message

Revision ID: 1bb060536ba5
Revises: 06b5dbdc7150
Create Date: 2020-04-28 16:29:54.260185

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1bb060536ba5'
down_revision = '06b5dbdc7150'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lead_requests')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lead_requests',
    sa.Column('query_date', mysql.DATETIME(), nullable=True),
    sa.Column('company_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('company_lead_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('contact_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('contact_lead_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='lead_requests_ibfk_4'),
    sa.ForeignKeyConstraint(['company_lead_id'], ['company_leads.id'], name='lead_requests_ibfk_3'),
    sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], name='lead_requests_ibfk_1'),
    sa.ForeignKeyConstraint(['contact_lead_id'], ['contact_leads.id'], name='lead_requests_ibfk_2'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='lead_requests_ibfk_5'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###