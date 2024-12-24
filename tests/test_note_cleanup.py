import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Note, NoteMetadata, User
from app.usecases.note.note import delete_old_notes
from app.database.schemas.note import NoteCreate, NoteMetadataCreate
from app.usecases.note.note import add_note
from app.database.schemas.user import UserCreate
from app.usecases.user.user import create_user

class TestNoteCleanup(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        
        # Create a test user
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword"
        )
        self.test_user = create_user(self.db, user_data)
        
    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def create_test_note(self, created_at: datetime, content_url: str = None) -> Note:
        """Helper method to create a test note"""
        note_create = NoteCreate(
            title="Test Note",
            summary="Test Summary",
            transcript_text="Test Transcript",
            language="en",
            content_url=content_url
        )
        
        note = add_note(
            db=self.db,
            user_id=self.test_user.id,
            folder_id=None,
            note_create=note_create
        )
        
        # Manually set the created_at date for testing
        note.created_at = created_at
        self.db.commit()
        
        # Add metadata
        metadata_create = NoteMetadataCreate(
            title="Test Note",
            content_category="test",
            emoji_representation="📝",
            date_created=created_at
        )
        
        metadata = NoteMetadata(
            note_id=note.id,
            user_id=self.test_user.id,
            **metadata_create.dict()
        )
        self.db.add(metadata)
        self.db.commit()
        
        return note

    def test_delete_old_notes(self):
        try:
            # Create notes with different dates
            now = datetime.now()
            
            # Create an old note (4 months ago)
            old_note = self.create_test_note(
                created_at=now - timedelta(days=120),
                content_url="https://test.com/old.mp3"
            )
            
            # Create a recent note (1 month ago)
            recent_note = self.create_test_note(
                created_at=now - timedelta(days=30),
                content_url="https://test.com/recent.mp3"
            )
            
            # Run the cleanup
            result = delete_old_notes(self.db)
            
            # Add debugging
            if not result["success"]:
                print(f"Delete operation failed: {result.get('errors', [])}")
                
            # Verify the results
            self.assertTrue(result["success"])
            self.assertEqual(result["deleted_count"], 1)
        except Exception as e:
            print(f"Test failed with error: {str(e)}")
            raise

    def test_delete_notes_with_invalid_minio_files(self):
        """Test cleanup handling when MinIO file deletion fails"""
        # Create an old note with an invalid content URL
        old_note = self.create_test_note(
            created_at=datetime.now() - timedelta(days=120),
            content_url="https://test.com/nonexistent.mp3"
        )
        
        # Run the cleanup
        result = delete_old_notes(self.db)
        
        # Verify the results
        self.assertTrue(result["success"])
        self.assertEqual(result["deleted_count"], 1)  # Note should be deleted even if file deletion fails
        self.assertTrue(len(result["errors"]) > 0)  # Should have an error for failed file deletion
        
        # Verify the note was deleted from database
        note_check = self.db.query(Note).filter(Note.id == old_note.id).first()
        self.assertIsNone(note_check)

    def test_no_old_notes(self):
        """Test cleanup when there are no old notes"""
        # Create only recent notes
        recent_note = self.create_test_note(
            created_at=datetime.now() - timedelta(days=30)
        )
        
        # Run the cleanup
        result = delete_old_notes(self.db)
        
        # Verify the results
        self.assertTrue(result["success"])
        self.assertEqual(result["deleted_count"], 0)  # No notes should be deleted
        self.assertEqual(len(result["errors"]), 0)  # No errors should occur
        
        # Verify the recent note still exists
        note_check = self.db.query(Note).filter(Note.id == recent_note.id).first()
        self.assertIsNotNone(note_check)

if __name__ == '__main__':
    unittest.main()