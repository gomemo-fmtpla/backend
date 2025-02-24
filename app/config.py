from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Redis settings
    REDIS_URL: str = "redis://redis:6380/0"
    
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
    
    # MinIO settings
    MINIO_ENDPOINTS: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    
    # Proxy settings
    PROXY_URL: str = "http://localhost:3128"
    
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra='allow'
    )

settings = Settings()