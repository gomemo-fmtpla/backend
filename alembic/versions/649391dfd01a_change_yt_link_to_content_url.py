"""change yt link to content url

Revision ID: 649391dfd01a
Revises: daa4d6319534
Create Date: 2024-08-26 23:30:55.042529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '649391dfd01a'
down_revision: Union[str, None] = 'daa4d6319534'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('content_url', sa.String(length=255), nullable=True))
    op.drop_column('notes', 'youtube_link')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('youtube_link', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('notes', 'content_url')
    # ### end Alembic commands ###
