# `user_backend`

## Responsibilities

- User lifecycle: register, login, MFA, password resets.
- Expose catalog of available agents (read-only).
- CRUD operations for agent instances, writing to `shared_psql`.
- WebSocket gateway that streams instance state updates from RabbitMQ events.
- Orchestrate Celery tasks for long-running workflows (shared Flower instance monitors only this service and `admin_backend`).

## Data Stores

- `user_psql`: owns user/account tables.
- `shared_psql`: read/write for instances (foreign ownership). Changes must publish events.
- `user_redis`: cache + Celery backend.
- `packages/shared_psql_models`: import `Base`, `Agent`, and `Instance` definitions instead of redefining shared tables locally.

## Shared Schema Workflow

- Point Alembic's `target_metadata` at `shared_psql_models.Base.metadata`.
- When the shared package changes, regenerate this service's migrations and update docs per `docs/services/shared_psql_models.md`.

## Event Integration

- Publishes `instance.created`, `instance.updated`, `instance.deleted` through `event_broker`.
- Subscribes to `instance.updated` to push to clients.

## Testing

- Unit tests under `services/user_backend/tests`.
- Contract tests for event payloads should live in `tests/contracts`.


