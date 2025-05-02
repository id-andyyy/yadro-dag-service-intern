from pydantic_settings import BaseSettings
from pydantic import Extra


class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = Extra.ignore


settings = Settings()
