from typing import Dict
from app.database.models import Note, NoteMetadata


def note_to_dict(note: Note) -> Dict:
    return {
        "id": note.id,
        "user_id": note.user_id,
        "folder_id": note.folder_id,
        "content_url": note.content_url,
        "title": note.title,
        "summary": note.summary,
        "transcript_text": note.transcript_text,
        "language": note.language,
        "flashcards": note.flashcards,
        "quizzes": note.quizzes,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        # Add other fields as needed
    }

def metadata_to_dict(metadata: NoteMetadata) -> Dict:
    return {
        "note_id": metadata.note_id,
        "title": metadata.title,
        "content_category": metadata.content_category,
        "date_created": metadata.date_created.isoformat() if metadata.date_created else None,
        "user_id": metadata.user_id,
        "folder_id": metadata.folder_id,
        "emoji_representation": metadata.emoji_representation,
    }