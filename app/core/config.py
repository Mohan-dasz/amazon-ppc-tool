# core/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # loads .env from project root

class Settings:
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("1","true","yes")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")

    HELIUM10_EMAIL: str | None = os.getenv("HELIUM10_EMAIL")
    HELIUM10_PASSWORD: str | None = os.getenv("HELIUM10_PASSWORD")
    HELIUM10_USER_DATA_DIR: str = os.path.expanduser(os.getenv("HELIUM10_USER_DATA_DIR", "~/.cache/helium10_profile"))
    HELIUM10_HEADLESS: bool = os.getenv("HELIUM10_HEADLESS", "True").lower() in ("1","true","yes")

settings = Settings()
