import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tgrt_full_stack_technical_task.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    WATERMARK_TEXT = os.getenv("WATERMARK_TEXT", "News Extractor")

settings = Settings()