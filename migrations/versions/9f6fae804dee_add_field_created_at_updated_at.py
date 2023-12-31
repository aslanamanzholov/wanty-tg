"""add field created_at, updated_at

Revision ID: 9f6fae804dee
Revises: ab9a166dde12
Create Date: 2023-12-06 16:10:20.137216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f6fae804dee'
down_revision = 'ab9a166dde12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dream', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('dream', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('dreamlikedrecord', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('dreamlikedrecord', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('user', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'updated_at')
    op.drop_column('user', 'created_at')
    op.drop_column('dreamlikedrecord', 'updated_at')
    op.drop_column('dreamlikedrecord', 'created_at')
    op.drop_column('dream', 'updated_at')
    op.drop_column('dream', 'created_at')
    # ### end Alembic commands ###
