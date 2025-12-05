# Botberi Backend Platform

This repository contains the infrastructure and service scaffolding for the Botberi platform. The system is intentionally structured as a multi-service FastAPI monorepo so that additional teams can extend it with minimal friction.

## High-Level Goals

- Separation of concerns between _user_, _admin_, and _shared_ surfaces.
- Async-first communication through RabbitMQ (`event_bus`) with an internal `event_broker` FastAPI service to keep event contracts centralized.
- Postgres is split into `user_psql` (user/account data) and `shared_psql` (agents/instances) to keep ownership boundaries clear.
- `packages/shared_psql_models` is the canonical SQLAlchemy/Pydantic package for every table stored in `shared_psql`, preventing schema drift across services.
- Only `user_backend` and `admin_backend` run Celery workers for long-running jobs, all of which are monitored via Flower (`:4400`) and (future) Grafana dashboards.
- Everything runs in Docker; dev/prod configurations share the same compose topology but different `.env` files.

## Services & Ports

| Service               | Type     | Port       | Notes                                                                    |
| --------------------- | -------- | ---------- | ------------------------------------------------------------------------ |
| `user_backend`        | FastAPI  | 8010       | User auth, agent catalogs, instance lifecycle.                           |
| `admin_backend`       | FastAPI  | 8020       | Administrative tooling and audit features.                               |
| `event_broker`        | FastAPI  | 8030       | Normalizes Postgres NOTIFY payloads into RabbitMQ events and vice versa. |
| `user_psql`           | Postgres | 5430       | Stores user/auth data only.                                              |
| `shared_psql`         | Postgres | 5440       | Stores agent definitions and instances.                                  |
| `user_redis`          | Redis    | 6600       | Cache + Celery broker for user backend jobs.                             |
| `event_bus`           | RabbitMQ | 5672/15672 | Event backbone (5672) + management UI (15672).                           |
| `celery_worker`       | Celery   | —          | Executes queues owned by `user_backend` (admin worker will mirror it).   |
| `flower`              | Flower   | 4400       | Monitors Celery queues for user/admin backends only.                     |
| `network`             | Nginx    | 8080       | Edge router/WS termination.                                              |

See `docs/architecture/overview.md` for a deeper dive.

## Development Quickstart

1. Copy environment templates if you need to override defaults:
   ```powershell
   Get-ChildItem environments/dev -Filter *.env.example | ForEach-Object {
       Copy-Item $_.FullName ($_.FullName -replace '\.example$', '') -Force
   }
   ```
2. Install the shared schema package locally so every service can import `shared_psql_models`:
   ```powershell
   pip install -e packages/shared_psql_models
   ```
3. Start the stack:
   ```powershell
   docker compose -f docker-compose.dev.yml --env-file environments/dev/dev.env.example up --build
   ```
4. Visit:
   - Swagger: `http://localhost:8010/docs`, `http://localhost:8020/docs`
   - Flower: `http://localhost:4400`
   - RabbitMQ UI: `http://localhost:15672`

## Documentation-First Workflow

- All service contracts, event schemas, and data ownership notes live under `./docs`.
- Shared schema guidance lives in `docs/services/shared_psql_models.md`; read it before changing anything under `packages/shared_psql_models`.
- The agents/instances lifecycle—including status enums and cross-service workflows—is captured in `docs/architecture/agents.md`. Update it before or alongside any behavioral change.
- `llms.txt` describes the guardrails for any coding agent touching this repo—**read it before contributing**.
- Each change that alters a database schema **must** include Alembic migrations for the affected service.

## Testing & CI Foundation

- `pytest` is the canonical runner; each service keeps its own test suite under `services/<service>/tests`.
- `ruff` enforces formatting + linting, configured at the repo root.
- CI will later gate on lint + unit tests + type checks; set up scripts in `docs/operations/testing.md`.

## Next Steps

1. Flesh out the FastAPI routers with real business logic per service.
2. Implement actual SQLAlchemy models/migrations for users, agents, and instances.
3. Formalize the RabbitMQ event catalog and back it with contract tests.
4. Add CI workflows (GitHub Actions) for linting, tests, image builds, and vulnerability scanning.
