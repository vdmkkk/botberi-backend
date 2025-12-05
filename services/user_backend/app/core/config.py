from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "user_backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://localhost:5432/botberi_users"
    sync_database_url: str = "postgresql+psycopg://localhost:5432/botberi_users"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    celery_default_queue: str = "user_default"
    shared_pg_dsn: str | None = None
    jwt_secret: str = "local-secret"
    jwt_alg: str = "HS256"

    model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8", extra="allow")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


