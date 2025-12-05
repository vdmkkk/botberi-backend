# Agents & Instances Domain

This document captures the cross-service business logic for agents, the instances users create from them, and how state changes propagate through the platform. Update this file whenever the lifecycle, ownership, or notification rules evolve.

## Entities & Ownership

| Entity    | Stored In      | Owner Service    | Notes                                                                 |
| --------- | -------------- | ---------------- | --------------------------------------------------------------------- |
| Agent         | `shared_psql`  | `admin_backend`  | Admins own CRUD for catalog entries.                                   |
| Instance      | `shared_psql`  | `user_backend`   | Rows reference `bot_id` + `user_id` (from `user_psql`).                |
| KnowledgeBase | `shared_psql`  | `user_backend`   | One-to-one per instance, stores KB entries.                            |
| User          | `user_psql`    | `user_backend`   | Authentication + profile data only.                                   |

- `user_psql` **must never** store agent/instance information.
- `shared_psql` is intentionally shared so `agents_worker` (ML workflows) can react to changes without going through user/admin APIs.
- SQLAlchemy + Pydantic primitives for agents/instances are defined once inside `packages/shared_psql_models`; keep services thin by importing from there.

### Agent Schema (`agents` table)

| Column           | Type   | Notes                                   |
| ---------------- | ------ | --------------------------------------- |
| `id`             | serial | Primary key (auto increment).           |
| `title`          | text   | Display name shown to admins/users.     |
| `content`        | jsonb  | Arbitrary metadata (capabilities, etc.) |
| `activation_code`| text   | Unique code referenced by downstream ML |
| `rate`           | int    | Internal weighting / pricing metric.    |

- Table + models defined once in `packages/shared_psql_models` (see version `0.3.0`).
- All services should treat `content` as an opaque document owned by the admin tooling.

### Instance & Knowledge Base Schema

| Table                 | Columns (highlights)                                                                                         | Notes                                           |
| --------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- |
| `instances`           | `id`, `bot_id` (FK -> `agents`), `user_id`, `title`, `user_config` (jsonb), `pipeline_config` (jsonb), status | Created by `user_backend`.                      |
| `knowledge_bases`     | `id`, `instance_id` (unique FK)                                                                              | Auto-created with each instance.                |
| `knowledge_base_entries` | `id`, `knowledge_base_id`, `content`, `data_type`, `lang_hint`, `status`                                  | User-managed KB entries per instance.           |

Enums live in the shared package and must be updated everywhere when values change:

- `InstanceStatus`: `pending`, `provisioning`, `running`, `failed`, `stopped`.
- `KBEntryStatus`: `queued`, `processing`, `ready`, `failed`.
- `KBDataType`: `document`, `video`, `other`.
- `KBLangHint`: `en`, `es`, `other`.

### Service capabilities

- `admin_backend`: full CRUD (`/api/v1/agents`) including activation code changes and deletion. Every mutation must flow through this API to keep the catalog authoritative.
- `user_backend`: read-only catalog APIs (`/api/v1/agents`, `/api/v1/agents/{id}`) so frontends can display available agents. It also owns instance + knowledge base CRUD (`/api/v1/instances`, `/api/v1/instances/{id}/knowledge-base/...`) but **never** mutates agent rows.

## Lifecycle (Happy Path)

1. User authenticates via `user_backend` (data in `user_psql`).
2. Frontend fetches available agents from `user_backend`, which proxies curated data from `shared_psql`.
3. User requests a new instance:
   - `user_backend` validates quotas, writes the new row into `shared_psql`, and returns a pending instance payload.
   - `shared_psql` trigger fires `NOTIFY instances_notify` with the inserted row.
4. `event_broker` listens to the channel, normalizes the payload, and publishes `instance.created` via RabbitMQ (`event_bus`).
5. `agents_worker` consumes the event, starts the n8n/ML pipeline, then updates the instance status (e.g., `running`), committing back to `shared_psql`.
6. The trigger emits another notification, `event_broker` publishes `instance.updated`, and `user_backend` fans it out to WebSocket clients.

Deletes follow the same pattern with `instance.deleted`, ensuring `agents_worker` tears down resources.

## Status Model

| Status          | Producer           | Meaning                                                              |
| --------------- | ------------------ | -------------------------------------------------------------------- |
| `pending`       | `user_backend`     | Instance row created; waiting for orchestration.                     |
| `provisioning`  | `agents_worker`    | ML workflows booting up / warming caches.                            |
| `running`       | `agents_worker`    | Pipeline finished successfully; instance is live.                    |
| `failed`        | `agents_worker`    | Provisioning or execution error; details recorded downstream.       |
| `stopped`       | `user_backend`     | User explicitly halted the instance.                                 |

KB entries follow `queued → processing → ready` or `failed`. Any change to these enums requires updating this file **and** the RabbitMQ event catalog (`docs/architecture/event_bus.md`).

## Event Responsibilities

- `event_broker` is the only service translating Postgres `NOTIFY` payloads into RabbitMQ events. Never bypass it.
- All new routing keys must be documented and versioned.
- Services consuming events must be idempotent; `agents_worker` should tolerate duplicate notifications.
- `user_backend` currently emits the first wave of events (`instance.created`, `instance.updated`, `instance.deleted`, `knowledge_base.created`, `knowledge_base.entry.*`) so downstream services can react immediately even before NOTIFY bridges exist.

## Observability & Tooling

- Celery tasks that orchestrate instance side effects live in `user_backend` (`app/workers`) today; `admin_backend` will reuse the same pattern for administrative workflows, and no other service should introduce Celery.
- Flower (`:4400`) plus the Grafana dashboards in `infra/grafana` monitor only those user/admin queues.
- When adding new pipelines for either backend, ensure task/queue names are documented here and in `llms.txt` so other contributors know how to operate them.

## Future Services

`agents_worker` (FastAPI + Celery) is not implemented yet, but its write access to `shared_psql` and RabbitMQ queues is reserved. When that service is built, link its docs here and keep the lifecycle narrative in sync.


