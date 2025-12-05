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

## Agent Catalog API

- `GET /api/v1/agents`: fetches the entire catalog from `shared_psql` (via `shared_psql_models.Agent`), used by the frontend to render the marketplace.
- `GET /api/v1/agents/{id}`: fetch a single agent by primary key.
- These routes are **read-only**; writes go through `admin_backend`.
- Dependencies pull from `SHARED_PG_DSN` using `app.db.shared_session`. Keep this DSN configured in both dev/prod env templates.

## Instance & Knowledge Base API

- `POST /api/v1/instances`: validates the agent (`bot_id`), creates the instance row + an empty knowledge base, emits `instance.created` and `knowledge_base.created`.
- `GET /api/v1/instances` / `GET /api/v1/instances/{id}`: list or fetch the caller's instances (scoped by `user_id`).
- `PATCH /api/v1/instances/{id}`: update `title`, `user_config`, or `pipeline_config`; emits `instance.updated`.
- `DELETE /api/v1/instances/{id}`: cascades knowledge base + entries, emits `instance.deleted`.
- Knowledge base management lives under `/api/v1/instances/{id}/knowledge-base/entries` (create/list/delete). Every mutation emits the corresponding `knowledge_base.entry.*` event.
- All writes occur in `shared_psql` via `shared_psql_models` + the shared session helper. Never touch agent tables from this service.

## Event Integration

- Publishes `instance.created`, `instance.updated`, `instance.deleted` through `event_broker`.
- Subscribes to `instance.updated` to push to clients.
- Postgres triggers (`notify_domain_event`) fire on every insert/update/delete for `instances`, `knowledge_bases`, and `knowledge_base_entries`. `event_broker` listens on `instances_notify` and republishes to RabbitMQ, so API code no longer emits events directly.

## Testing

- Unit tests under `services/user_backend/tests`.
- Contract tests for event payloads should live in `tests/contracts`.


