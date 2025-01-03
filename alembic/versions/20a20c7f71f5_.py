"""

Revision ID: 20a20c7f71f5
Revises: e2f0353d8e44
Create Date: 2024-09-08 07:18:16.715047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20a20c7f71f5'
down_revision: Union[str, None] = 'e2f0353d8e44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'subscription_plan',
               existing_type=postgresql.ENUM('free', 'weekly', 'monthly', 'annual', 'family', name='subscriptionplantype'),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'subscription_plan',
               existing_type=sa.String(),
               type_=postgresql.ENUM('free', 'weekly', 'monthly', 'annual', 'family', name='subscriptionplantype'),
               existing_nullable=False)
    # ### end Alembic commands ###
