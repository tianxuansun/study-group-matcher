from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Study Group Matcher"
    DATABASE_URL: str = "sqlite:///./dev.db"  # Week 3 can switch to Postgres
    class Config:
        env_file = ".env"

settings = Settings()
