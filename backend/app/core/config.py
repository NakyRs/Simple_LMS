from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTE: int= 60* 28* 8
    SECRET_KEY: str = secrets.token_urlsafe(32)

settings = Settings()