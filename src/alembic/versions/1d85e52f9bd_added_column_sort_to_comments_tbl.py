"""Added column sort to comments tbl

Revision ID: 1d85e52f9bd
Revises: 55d46b38fa3
Create Date: 2014-05-27 18:04:30.713592

"""

# revision identifiers, used by Alembic.
revision = '1d85e52f9bd'
down_revision = '55d46b38fa3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('sort', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comments', 'sort')
    ### end Alembic commands ###