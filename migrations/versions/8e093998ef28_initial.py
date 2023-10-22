"""initial

Revision ID: 8e093998ef28
Revises: 
Create Date: 2023-10-21 22:55:51.661366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e093998ef28'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('user_name', sa.Text(), nullable=True),
    sa.Column('age', sa.SmallInteger(), nullable=True),
    sa.Column('gender', sa.Text(), nullable=True),
    sa.Column('country', sa.Text(), nullable=True),
    sa.Column('role', sa.Enum('USER', 'MODERATOR', 'ADMINISTRATOR', name='role'), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('user_id', name=op.f('uq_user_user_id'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
