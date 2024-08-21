from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Singleton pattern to ensure only one instance of the database connection
class DatabaseSingleton:
    __instance = None

    @staticmethod
    def getInstance():
        if DatabaseSingleton.__instance is None:
            DatabaseSingleton()
        return DatabaseSingleton.__instance

    def __init__(self):
        if DatabaseSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.engine = create_engine(os.getenv("DATABASE_URL", "postgresql://user:password@localhost/mydb"))
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.Base = declarative_base()
            DatabaseSingleton.__instance = self

# Get the database session
def get_db():
    db = DatabaseSingleton.getInstance().SessionLocal()
    try:
        yield db
    finally:
        db.close()