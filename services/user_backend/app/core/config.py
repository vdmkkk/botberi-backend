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
    jwt_access_ttl_seconds: int = 3600
    auth_cookie_name: str = "botberi_session"
    registration_code_ttl_seconds: int = 900
    registration_code_cooldown_seconds: int = 60
    password_reset_ttl_seconds: int = 1800
    password_reset_url_template: str = "https://app.local/reset-password?token={token}"
    email_sender: str = "no-reply@botberi.local"
    verification_email_subject: str = "Complete your Botberi signup"
    password_reset_email_subject: str = "Botberi password reset"
    frontend_profile_url: str = "https://app.local/profile"
    event_exchange: str = "events.topic"
    event_emit_enabled: bool = True

    model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8", extra="allow")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


