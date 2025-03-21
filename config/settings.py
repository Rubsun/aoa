from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_CHAT_ID: str

    class Config:
        env_file = '/home/maksim/PycharmProjects/changer_bot/config/.env'


settings = Settings()
