# app/usecases/note.py

from datetime import datetime, timedelta
from app.usecases.storage.audio_store import delete_object, extract_audio_filename
from sqlalchemy.orm import Session
from app.database.models import Folder, Note, NoteMetadata, User
from app.database.schemas.note import NoteCreate, NoteMetadataCreate, NoteMetadataUpdate, NoteUpdate
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

def add_note(
    db: Session, 
    user_id: int, 
    folder_id: Optional[int], 
    note_create: NoteCreate
) -> Note:
    try:
        new_note = Note(
            user_id=user_id,
            folder_id=folder_id,
            **note_create.dict()  # Unpack the Pydantic model to pass parameters
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return new_note
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def update_note(
    db: Session, 
    note_id: int, 
    note_update: NoteUpdate,
    user_id : int
) -> Optional[Note]:
    try:
        note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
        note_metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note_id, NoteMetadata.user_id == user_id).first()
        if not note or not note_metadata:
            return None
        for field, value in note_update.dict(exclude_unset=True).items():
            if field == "title" : 
                setattr(note_metadata, field, value)
            setattr(note, field, value)
        db.commit()
        db.refresh(note)
        db.refresh(note_metadata)
        return note
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def add_metadata(
    db: Session, 
    user_id: int,
    note_id: int, 
    metadata_create: NoteMetadataCreate
) -> NoteMetadata:
    try:
        new_metadata = NoteMetadata(
            user_id=user_id,
            note_id=note_id,
            **metadata_create.dict()
        )
        db.add(new_metadata)
        db.commit()
        db.refresh(new_metadata)
        return new_metadata
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def create_welcoming_note(db : Session, user_id : int) :
    welcomeNoteSummary = (
        "# Introduction to Gomemo 📝\n\n"
        "## Overview\n"
        "- Gomemo is an AI note-taker that turns any *audio* into organized notes, flashcards, quizzes, and more.\n"
        "- Available for iPhone and iPad.\n\n"
        "## Does Gomemo actually work?\n"
        "- **Thousands of students** have told us - in our ratings - that Gomemo helped them *ace a final exam*, *learn course materials faster*, and generally improve their grades.\n"
        "- **Hundreds of parents** have gifted Gomemo to their kids in school to help improve their grades.\n"
        "- Now, even **young professionals** are using Gomemo to record meetings and audio with instant AI-written summaries on-the-go.\n\n"
        "## Create a Note\n\n"
        "1. **Upload Audio**\n"
        "   - Process: Tap upload -> Select file -> Auto-detect language.\n"
        "   - Step-by-step guidance available for importing from the iPhone voice memo app.\n"
        "2. **Record Audio**\n"
        "   - Start recording by tapping the record button.\n"
        "   - Specify the topic for better quality notes!\n"
        "   - Recording tips: Leave the app open while recording to ensure the best audio quality. The safest audio recordings are under 90 minutes - above 90 minutes, you are more likely to experience an error (we're working to improve this, always!).\n\n"
        "## Review Notes\n"
        "- Notes include chapter headings, subheadings, and key takeaways.\n"
        "- Note: Transcript editing is currently not available.\n\n"
        "## Additional Features\n\n"
        "### Quizzes and Flashcards\n"
        "- Quizzes: Automatically generated based on the notes.\n"
        "- Flashcards: Created from the audio recordings.\n\n"
        "### Translation\n"
        "- Supports translation to/from 100 languages.\n"
        "- Real-time note translation available.\n\n"
        "## Gomemo Unlimited Pass\n"
        "- **Unlimited Pass** lets you create unlimited notes, flashcards, and quizzes with Gomemo for one price.\n"
        "- **Save 75%** on your pass by subscribing to the annual pass. Monthly and weekly options are available at a higher price per week.\n"
        "- **Yes, it works.** 😄\n\n"
        "## Support & Help\n"
        "- The creators of Gomemo would love to hear from you. Tap the 'contact' button to send a message. We read every single message.\n\n"
        "Gomemo loves you 🫶\n"
    )

    welcomeNoteTranscript = """
        Gomemo is an AI note-taker that turns any audio into organized notes, flashcards, quizzes, and more. It is available for iPhone and iPad. Thousands of students have reported, in our ratings, that Gomemo helped them ace final exams, learn course materials faster, and generally improve their grades. Hundreds of parents have gifted Gomemo to their kids in school to help improve their academic performance. Young professionals are also using Gomemo to record meetings and audio, with instant AI-written summaries available on-the-go.

        To create a note, you can either upload audio or record it. For uploading audio, tap 'upload', select the file, and use the auto-detect language option. Step-by-step guidance is available for importing from the iPhone voice memo app. For recording audio, simply tap the record button and specify the topic for better quality notes. To ensure the best audio quality, leave the app open while recording. The safest audio recordings are under 90 minutes. For longer recordings, there is a higher chance of errors, but we are constantly working to improve this.

        The notes generated by Gomemo include chapter headings, subheadings, and key takeaways. However, transcript editing is currently not available. 

        Gomemo also offers quizzes and flashcards that are automatically generated based on the notes. Flashcards can be created from the audio recordings. Additionally, Gomemo supports translation to and from 100 languages, with real-time note translation available.

        The Gomemo Unlimited Pass allows you to create unlimited notes, flashcards, and quizzes for one price. By subscribing to the annual pass, you can save 75%. Monthly and weekly options are also available, although they come at a higher price per week. 

        If you need help or support, the creators of Gomemo are eager to hear from you. Tap the 'contact' button to send a message. We read every single message.

        Gomemo loves you.
        """


    note_create = NoteCreate(
                title="Welcome to Gomemo",
                summary=welcomeNoteSummary,
                transcript_text=welcomeNoteTranscript,
                language="English",
                content_url="",
            )
    
    note = add_note(db=db, user_id=user_id, folder_id=None, note_create=note_create) 
    
    metadata_create = NoteMetadataCreate(
        title="Welcome to Gomemo",
        content_category="Introduction",
        emoji_representation="🙌",
        date_created=datetime.now()
    )

    metadata = add_metadata(db=db, user_id=user_id, note_id=note.id, metadata_create=metadata_create)
    
    return metadata.note_id

def update_metadata(
    db: Session, 
    note_id: int, 
    metadata_update: NoteMetadataUpdate
) -> Optional[NoteMetadata]:
    try:
        metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note_id).first()
        if not metadata:
            return None
        for field, value in metadata_update.dict(exclude_unset=True).items():
            setattr(metadata, field, value)
        db.commit()
        db.refresh(metadata)
        return metadata
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
def move_note_to_folder_usecase(db: Session, note_id: int, new_folder_id: Optional[int]) -> Note:
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        note.folder_id = new_folder_id
        db.commit()
        db.refresh(note)
        return note
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def remove_note_folder_usecase(db: Session, note_id: int) -> Note:
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        note.folder_id = None
        db.commit()
        db.refresh(note)
        return note
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def get_all_notes(db: Session, user_id: int) -> List[NoteMetadata]:
    return db.query(NoteMetadata).filter(NoteMetadata.user_id == user_id).all()

def get_unfoldered_notes(db: Session, user_id: int) -> List[Note]:
    return db.query(Note).filter(Note.user_id == user_id, Note.folder_id == None).all()

def get_notes_by_folder(db: Session, folder_id: int) -> List[Note]:
    return db.query(Note).filter(Note.folder_id == folder_id).all()

def get_note_by_id(db: Session, note_id: int, user_id: int) -> Note:
    return db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()

def get_folder_by_note_id_usecase(db: Session, note_id: int, user_id: int) -> Note:
    try:
        note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
        if note:
            return db.query(Folder).filter(Folder.id == note.folder_id).first()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
def delete_old_notes(db: Session) -> dict:
    try:
        three_months_ago = datetime.now() - timedelta(days=90)
        old_notes = db.query(Note).filter(Note.created_at < three_months_ago).all()
        
        deleted_count = 0
        errors = []
        
        for note in old_notes:
            try:
                # First delete associated metadata
                metadata = db.query(NoteMetadata).filter(NoteMetadata.note_id == note.id).first()
                if metadata:
                    db.delete(metadata)
                
                # Then handle the file deletion
                if note.content_url:
                    try:
                        filename = extract_audio_filename(note.content_url)
                        if filename:
                            try:
                                delete_object(filename)
                            except Exception as e:
                                errors.append(f"Failed to delete MinIO file for note {note.id}: {str(e)}")
                                # Continue with note deletion even if file deletion fails
                    except Exception as e:
                        errors.append(f"Failed to process content URL for note {note.id}: {str(e)}")
                
                # Finally delete the note
                db.delete(note)
                deleted_count += 1
                
                # Commit after each successful deletion
                db.commit()
                
            except Exception as e:
                db.rollback()
                errors.append(f"Failed to delete note {note.id}: {str(e)}")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "errors": errors
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "deleted_count": 0,
            "errors": [str(e)]
        }