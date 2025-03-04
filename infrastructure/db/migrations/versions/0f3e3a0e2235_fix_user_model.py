"""Fix user model

Revision ID: 0f3e3a0e2235
Revises: 20240206123456
Create Date: 2025-02-06 23:44:33.851074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0f3e3a0e2235'
down_revision: Union[str, None] = '20240206123456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('phone_number', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('role', sa.VARCHAR(length=50), server_default=sa.text("'user'::character varying"), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('user_id', name='users_pkey'),
    sa.UniqueConstraint('email', name='users_email_key')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    # ### end Alembic commands ###
