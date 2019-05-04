"""markdown post

Revision ID: 6d361fdef31e
Revises: e488492eb10c
Create Date: 2019-05-04 21:17:10.792380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d361fdef31e'
down_revision = 'e488492eb10c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('body_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'body_html')
    # ### end Alembic commands ###