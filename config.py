import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    ADMIN_ID = os.getenv("ADMIN_ID")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.TELEGRAM_API_ID: missing.append("TELEGRAM_API_ID")
        if not cls.TELEGRAM_API_HASH: missing.append("TELEGRAM_API_HASH")
        if not cls.TELEGRAM_PHONE: missing.append("TELEGRAM_PHONE")
        if not cls.GEMINI_API_KEY: missing.append("GEMINI_API_KEY")
        if not cls.TELEGRAM_BOT_TOKEN: missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.OPENROUTER_API_KEY: missing.append("OPENROUTER_API_KEY")
        if not cls.ADMIN_ID: missing.append("ADMIN_ID")
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
        
        try:
            cls.TELEGRAM_API_ID = int(cls.TELEGRAM_API_ID)
            cls.ADMIN_ID = int(cls.ADMIN_ID)
        except ValueError:
            raise ValueError("TELEGRAM_API_ID and ADMIN_ID must be integers")

config = Config()
