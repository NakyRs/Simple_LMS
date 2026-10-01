from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from pydantic import EmailStr
from typing import Literal
from sqlalchemy import URL

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    ENVIRONMENT: Literal["dev", "prod"]|None= None
    DB_USER: str= ""
    DB_PASS: str= ""
    DB_HOST: str= "localhost"
    DB_PORT: int= 3306
    DB_NAME: str= ""

    @property
    def DATABASE_URL(self) -> URL:
        if self.ENVIRONMENT=="dev":
            return URL.create(
                drivername="sqlite",
                database="./dev.db"
            )
        return URL.create(
            drivername= "mysql+pymysql",
            username= self.DB_USER,
            password= self.DB_PASS,
            host= self.DB_HOST,
            port= self.DB_PORT,
            database= self.DB_NAME
        )
    
    ACCESS_TOKEN_EXPIRE_MINUTE: int= 60* 24* 8
    SECRET_KEY: str = secrets.token_urlsafe(32)

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

settings = Settings()