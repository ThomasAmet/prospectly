"""empty message

Revision ID: 0bb271735546
Revises: 516f07da7b6e
Create Date: 2020-04-07 21:09:29.786162

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0bb271735546'
down_revision = '516f07da7b6e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('leads')
    op.drop_table('subscriptions')
    op.add_column('lead_requests', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'lead_requests', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'lead_requests', type_='foreignkey')
    op.drop_column('lead_requests', 'user_id')
    op.create_table('subscriptions',
    sa.Column('plan_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('yearly', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('subscription_date', mysql.DATETIME(), nullable=True),
    sa.Column('next_payment', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name='subscriptions_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='subscriptions_ibfk_2'),
    sa.PrimaryKeyConstraint('plan_id', 'user_id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('leads',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('creation_date', mysql.DATETIME(), nullable=True),
    sa.Column('company_name', mysql.VARCHAR(length=120), nullable=True),
    sa.Column('company_address', mysql.VARCHAR(length=120), nullable=True),
    sa.Column('company_postal_code', mysql.VARCHAR(length=30), nullable=True),
    sa.Column('company_city', mysql.VARCHAR(length=60), nullable=True),
    sa.Column('company_email', mysql.VARCHAR(length=120), nullable=True),
    sa.Column('company_email_bcc', mysql.VARCHAR(length=120), nullable=True),
    sa.Column('company_phone', mysql.VARCHAR(length=60), nullable=True),
    sa.Column('company_activity_field', mysql.VARCHAR(length=60), nullable=False),
    sa.Column('owner_firstname', mysql.VARCHAR(length=60), nullable=True),
    sa.Column('owner_lastname', mysql.VARCHAR(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###