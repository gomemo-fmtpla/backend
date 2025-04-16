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
            # Fetch the environment variables
            db_user = os.getenv("DB_USER", "default_user")
            db_password = os.getenv("DB_PASSWORD", "default_password")
            db_host = os.getenv("DB_HOST", "localhost")
            db_name = os.getenv("DB_NAME", "default_db")

            # Construct the DATABASE_URL
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
            
            # Konfigurasi connection pool yang lebih baik
            # Meningkatkan max_overflow dan menambahkan parameter lain
            self.engine = create_engine(
                database_url, 
                pool_pre_ping=True,  # Cek koneksi sebelum digunakan
                pool_recycle=1800,   # Recycle koneksi setiap 30 menit
                pool_use_lifo=True,  # Gunakan koneksi terakhir yang dikembalikan (mengurangi jumlah koneksi aktif)
                pool_size=10,        # Default 5, ditingkatkan ke 10
                max_overflow=20,     # Default 10, ditingkatkan ke 20 
                pool_timeout=60      # Default 30, ditingkatkan ke 60 detik
            )

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