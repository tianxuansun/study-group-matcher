from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Study Group Matcher"
    DATABASE_URL: str = "sqlite:///./dev.db"

    # API-key gating (off by default)
    REQUIRE_API_KEY: bool = False
    API_KEY: str | None = None

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
