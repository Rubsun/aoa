from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_CHAT_ID: str

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"


settings = Settings()
