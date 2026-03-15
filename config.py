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
    TELEGRAM_SESSION_STRING = os.getenv("TELEGRAM_SESSION_STRING")

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
        
        # Specifically check for SESSION_STRING for server/Railway deployments
        if not cls.TELEGRAM_SESSION_STRING:
            print("⚠️ WARNING: TELEGRAM_SESSION_STRING is missing. For Railway or server deployments, you MUST provide it to avoid EOFError during login.")
        
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
        
        try:
            cls.TELEGRAM_API_ID = int(cls.TELEGRAM_API_ID)
            cls.ADMIN_ID = int(cls.ADMIN_ID)
        except ValueError:
            raise ValueError("TELEGRAM_API_ID and ADMIN_ID must be integers")

config = Config()
# Validate immediately so we catch missing env vars at import time
config.validate()
