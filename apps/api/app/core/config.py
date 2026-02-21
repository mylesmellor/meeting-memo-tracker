import json
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_BYTES: int = 10_485_760
    MAX_TRANSCRIPT_CHARS: int = 50_000

    AWS_S3_BUCKET: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_ENDPOINT_URL: Optional[str] = None

    ALLOWED_ORIGINS: str = '["http://localhost:3000"]'
    RATE_LIMIT_GENERATE: str = "10/hour"
    APP_ENV: str = "development"

    @property
    def allowed_origins_list(self) -> list[str]:
        return json.loads(self.ALLOWED_ORIGINS)


settings = Settings()
