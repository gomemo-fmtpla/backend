"""create note_links table

Revision ID: ef9f1cb2d7ef
Revises: 55fe4ec769a2
Create Date: 2024-10-23 21:57:01.752869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef9f1cb2d7ef'
down_revision: Union[str, None] = '55fe4ec769a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('note_links',
    sa.Column('note_link_id', sa.Integer(), nullable=False),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('date_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('note_link_id')
    )
    op.create_index(op.f('ix_note_links_note_link_id'), 'note_links', ['note_link_id'], unique=False)
    op.drop_table('audio_files')
    op.drop_index('idx_folders_user_id', table_name='folders')
    op.drop_index('idx_note_metadata_note_id', table_name='note_metadata')
    op.alter_column('notes', 'translated',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.drop_index('idx_notes_folder_id', table_name='notes')
    op.drop_index('idx_notes_user_id', table_name='notes')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('idx_notes_user_id', 'notes', ['user_id'], unique=False)
    op.create_index('idx_notes_folder_id', 'notes', ['folder_id'], unique=False)
    op.alter_column('notes', 'translated',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.create_index('idx_note_metadata_note_id', 'note_metadata', ['note_id'], unique=False)
    op.create_index('idx_folders_user_id', 'folders', ['user_id'], unique=False)
    op.create_table('audio_files',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('file_url', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='audio_files_pkey')
    )
    op.drop_index(op.f('ix_note_links_note_link_id'), table_name='note_links')
    op.drop_table('note_links')
    # ### end Alembic commands ###
