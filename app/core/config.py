from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Study Group Matcher"
    DATABASE_URL: str = "sqlite:///./dev.db"

    # Optional write protection for mutating endpoints.
    # When REQUIRE_API_KEY=true, requests must send:
    #   X-API-Key: <API_KEY>
    REQUIRE_API_KEY: bool = False
    API_KEY: str | None = None

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",  # ignore unknown env vars
    )


settings = Settings()
