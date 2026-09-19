from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from pydantic import EmailStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTE: int= 60* 24* 8
    SECRET_KEY: str = secrets.token_urlsafe(32)

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

settings = Settings()