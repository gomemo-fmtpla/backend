"""

Revision ID: 55fe4ec769a2
Revises: 20a20c7f71f5
Create Date: 2024-09-20 06:29:54.484264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55fe4ec769a2'
down_revision: Union[str, None] = '20a20c7f71f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('translated', sa.Boolean(), nullable=True))
    op.execute("UPDATE notes SET translated = false")
    op.alter_column('notes', 'translated', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notes', 'translated')
    # ### end Alembic commands ###
