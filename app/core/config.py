from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ===== APP =====
    APP_NAME: str = "wishlist"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_PORT: int = 8000

    # ===== DATABASE =====
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ===== JWT =====
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ===== REDIS =====
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ===== S3 =====
    S3_ACCESS_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("S3_ACCESS_KEY", "AWS_ACCESS_KEY"),
    )
    S3_SECRET_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("S3_SECRET_KEY", "AWS_SECRET_KEY"),
    )
    S3_REGION: str | None = Field(
        default=None,
        validation_alias=AliasChoices("S3_REGION", "AWS_REGION"),
    )
    S3_BUCKET_NAME: str | None = None

    S3_PUBLIC_BASE_URL: str | None = None
    S3_USE_PRESIGNED_URLS: bool = False
    S3_PRESIGNED_EXPIRES_SECONDS: int = 3600

    S3_PREFIX_AVATAR_USER: str = Field(
        default="uploads/avata-user",
        validation_alias=AliasChoices("S3_PREFIX_AVATAR_USER"),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
