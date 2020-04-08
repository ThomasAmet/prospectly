"""empty message

Revision ID: 198e01c77ac4
Revises: 009d1f1b3177
Create Date: 2020-04-03 00:42:41.616577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '198e01c77ac4'
down_revision = '009d1f1b3177'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('companies', sa.Column('countr', sa.String(length=60), nullable=True))
    op.add_column('contact_leads', sa.Column('facebook', sa.String(length=120), nullable=True))
    op.add_column('contact_leads', sa.Column('instagram', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('contact_leads', 'instagram')
    op.drop_column('contact_leads', 'facebook')
    op.drop_column('companies', 'countr')
    # ### end Alembic commands ###
