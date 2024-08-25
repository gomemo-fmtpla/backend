from typing import Dict
from app.database.models import Note


def note_to_dict(note: Note) -> Dict:
    return {
        "id": note.id,
        "user_id": note.user_id,
        "folder_id": note.folder_id,
        "youtube_link": note.youtube_link,
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