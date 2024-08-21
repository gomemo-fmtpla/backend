import unittest
from app.commons.environment_manager import load_env
from app.database.models import User
from app.database.schemas.user import UserCreate, UserUpdate
from app.database.db import get_db
from app.database.crud.user import create_user, get_user, update_user, delete_user

load_env()

class TestUserFunctions(unittest.TestCase):
    
    def setUp(self):
        # Set up a new database session for each test using the existing DatabaseSingleton
        self.db = next(get_db())

    def tearDown(self):
        # Rollback any changes made during the test and close the session
        self.db.rollback()
        self.db.close()
    
    def test_create_user(self):
        user_data = UserCreate(username="testuser", email="testuser@example.com", hashed_password="hashedpassword")
        created_user = create_user(self.db, user_data)
        
        self.assertIsNotNone(created_user.id)
        self.assertEqual(created_user.username, "testuser")
        self.assertEqual(created_user.email, "testuser@example.com")
    
    def test_get_user(self):
        user_data = UserCreate(username="testuser", email="testuser@example.com", hashed_password="hashedpassword")
        created_user = create_user(self.db, user_data)
        
        fetched_user = get_user(self.db, created_user.id)
        
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.username, "testuser")
    
    def test_update_user(self):
        user_data = UserCreate(username="testuser", email="testuser@example.com", hashed_password="hashedpassword")
        created_user = create_user(self.db, user_data)
        
        update_data = UserUpdate(username="updateduser", email="updateduser@example.com")
        updated_user = update_user(self.db, created_user.id, update_data)
        
        self.assertEqual(updated_user.username, "updateduser")
        self.assertEqual(updated_user.email, "updateduser@example.com")
    
    def test_delete_user(self):
        user_data = UserCreate(username="testuser", email="testuser@example.com", hashed_password="hashedpassword")
        created_user = create_user(self.db, user_data)
        
        deleted_user = delete_user(self.db, created_user.id)
        
        self.assertIsNotNone(deleted_user)
        self.assertIsNone(get_user(self.db, created_user.id))

if __name__ == "__main__":
    unittest.main()
