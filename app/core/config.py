import os
from typing import Optional

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/testdb")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QA Take-Home Exam API"
    VERSION: str = "1.0.0"
    
    # Database settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()