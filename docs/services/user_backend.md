# `user_backend`

## Responsibilities

- User lifecycle: register, login, MFA, password resets.
- Expose catalog of available agents (read-only).
- CRUD operations for agent instances, writing to `shared_psql`.
- WebSocket gateway that streams instance state updates from RabbitMQ events.
- Orchestrate Celery tasks for long-running workflows (shared Flower instance monitors only this service and `admin_backend`).
- Primary owner of the `users` table (see Alembic migrations + SQLAlchemy model).

## Data Stores

- `user_psql`: owns user/account tables.
- `shared_psql`: read/write for instances (foreign ownership). Changes must publish events.
- `user_redis`: cache + Celery backend.
- `packages/shared_psql_models`: import `Base`, `Agent`, and `Instance` definitions instead of redefining shared tables locally.

## Shared Schema Workflow

- Point Alembic's `target_metadata` at `shared_psql_models.Base.metadata`.
- When the shared package changes, regenerate this service's migrations and update docs per `docs/services/shared_psql_models.md`.

## Authentication API

- **Registration** is a two-step flow (`/auth/register/request` + `/auth/register/confirm`). Step one stores the pending payload + a 6-digit code in Redis (`registration:pending:<email>`) with TTL `REGISTRATION_CODE_TTL_SECONDS`. Cooldowns are enforced via `registration:cooldown:<email>`.
- **Email delivery** is currently logged through `app.services.notifications`; wire a transactional provider later. Subjects/body copy come from envs (`VERIFICATION_EMAIL_SUBJECT`, etc.).
- **Login** issues a JWT (`jwt_access_ttl_seconds`) and sets it both as an `HttpOnly` cookie (`AUTH_COOKIE_NAME`) and response header `X-Auth-Token`.
- **Password reset**: authenticated users call `/auth/password/reset/request`, which persists a slug in Redis with TTL `PASSWORD_RESET_TTL_SECONDS` and emails a link (`PASSWORD_RESET_URL_TEMPLATE`). `/auth/password/reset/confirm` consumes the slug and stores the new hash.
- **Profile updates** live under `/users/me` (GET/PATCH). Only non-service fields (`name`, `company`, `phone`, `telegram`) are mutable.

Redis is mandatory for throttling and slug TTLs—tests rely on `fakeredis`, but runtime should point to the `user_redis` container defined in Compose.

## Event Integration

- Publishes `instance.created`, `instance.updated`, `instance.deleted` through `event_broker`.
- Subscribes to `instance.updated` to push to clients.

## Testing

- Unit tests under `services/user_backend/tests`.
- Contract tests for event payloads should live in `tests/contracts`.


