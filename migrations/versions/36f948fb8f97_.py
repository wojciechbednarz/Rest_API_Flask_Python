"""empty message

Revision ID: 36f948fb8f97
Revises: bf7162521529
Create Date: 2024-07-07 22:25:34.334411

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '36f948fb8f97'
down_revision = 'bf7162521529'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(), nullable=False))
        batch_op.create_unique_constraint("email", ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint("email", type_='unique')
        batch_op.drop_column('email')

    # ### end Alembic commands ###
