from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "event_broker"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://shared_psql:5432/botberi_shared"
    sync_database_url: str = "postgresql+psycopg://shared_psql:5432/botberi_shared"
    listen_channel: str = "instances_notify"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    outgoing_exchange: str = "events.topic"

    model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8", extra="allow")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


