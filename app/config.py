from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/gomemo")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_IN_MIN: int = int(os.getenv("JWT_EXPIRES_IN_MIN", "60"))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6380/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6380/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6380/0")
    
    # App settings
    APP_NAME: str = "GoMemo"
    API_KEY: str = "fmtpla123"
    
    # Database settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "12345678"
    DB_HOST: str = "localhost:5432"
    DB_NAME: str = "gomemo"
    SSL_MODE: str = "require"
    
    # External services
    GOOGLE_APPLICATION_CREDENTIALS: str = "key.json"
    OPENAI_API_KEY: str
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_HEALTH_CHANNEL_ID: str = os.getenv("SLACK_HEALTH_CHANNEL_ID", "C0BBCFEAZN1")
    WHISPERX_BASE_URL: str = os.getenv(
        "WHISPERX_BASE_URL",
        "https://gomemo-whisperx.minutyshowpro.workers.dev",
    )
    
    # MinIO settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False") == "True"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "gomemo")
    
    # Proxy settings
    PROXY_URL: str = "http://localhost:3128"
    
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra='allow'
    )

settings = Settings()