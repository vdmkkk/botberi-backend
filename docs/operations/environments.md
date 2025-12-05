# Environment Strategy

## Files

- `environments/dev/.env` – compose-level overrides for local development.
- `environments/dev/*.env` – per-service env templates consumed via `env_file`.
- `environments/prod/.env` & counterparts – production defaults (never commit secrets).

## Variables

| Variable                                            | Description                           |
| --------------------------------------------------- | ------------------------------------- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Standard Postgres credentials.        |
| `DATABASE_URL`                                      | SQLAlchemy DSN used by FastAPI apps.  |
| `SYNC_DATABASE_URL`                                 | For Alembic migrations (sync driver). |
| `REDIS_URL`                                         | Redis endpoint for Celery + caching.  |
| `RABBITMQ_URL`                                      | AMQP connection string.               |
| `JWT_SECRET`, `JWT_ALG`                             | Auth tokens.                          |
| `JWT_ACCESS_TTL_SECONDS`                            | Expiry window for issued access JWTs. |
| `AUTH_COOKIE_NAME`                                  | Name of the HttpOnly cookie storing JWTs. |
| `REGISTRATION_CODE_TTL_SECONDS`                     | Lifetime of email verification codes. |
| `REGISTRATION_CODE_COOLDOWN_SECONDS`                | Cooldown before a user can request another code. |
| `PASSWORD_RESET_TTL_SECONDS`                        | Validity window for password reset slugs. |
| `PASSWORD_RESET_URL_TEMPLATE`                       | Frontend link template used in password reset emails. |
| `EMAIL_SENDER` / `VERIFICATION_EMAIL_SUBJECT` / `PASSWORD_RESET_EMAIL_SUBJECT` | Email metadata for transactional messages. |
| `FRONTEND_PROFILE_URL`                              | Used for linking out of emails/logs.  |
| `EVENT_EXCHANGE`, `EVENT_EMIT_ENABLED`              | RabbitMQ exchange name + toggle for emitting domain events. |

## Profiles

- **Dev:** verbose logging, auto-reload on FastAPI apps, seeded test data.
- **Prod:** gunicorn/uvicorn workers, health probes enabled, metrics shipped to Grafana/Prometheus.

## Shared Schema Package

- Before running any service locally, install the canonical `shared_psql_models` package with `pip install -e packages/shared_psql_models`.
- Docker images install this package automatically; local shells must do it manually so imports resolve and Alembic can read the shared metadata.

## Adding New Services

1. Create `environments/dev/<service>.env.example` and `environments/prod/<service>.env.example`.
2. Reference them in both compose files.
3. Document new variables in this file + `llms.txt` if global guidance is required.
