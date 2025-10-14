from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Study Group Matcher"
    DATABASE_URL: str = "sqlite:///./dev.db"
    model_config = ConfigDict(env_file=".env")

settings = Settings()