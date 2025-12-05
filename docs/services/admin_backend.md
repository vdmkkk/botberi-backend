# `admin_backend`

## Responsibilities

- Manage the catalog of publishable agents (draft, review, publish, retire).
- Audit trail for agent and instance changes.
- Administrative dashboards and tooling for support teams.
- Owns the admin-facing Celery queue (monitored via Flower alongside `user_backend`) for long-running review workflows.
- Full CRUD over shared agent definitions via `/api/v1/agents` (create/read/update/delete).

## Data Stores

- `shared_psql` is the source of truth for agents.
- `user_psql` is read-only for referencing users/owners.
- `packages/shared_psql_models` provides the only approved SQLAlchemy/Pydantic definitions for shared tables—always import from there.

## Shared Schema Workflow

- Alembic metadata must point to `shared_psql_models.Base.metadata`.
- Any change to the shared package requires new migrations here plus doc updates (see `docs/services/shared_psql_models.md`).

## Event Integration

- Publishes `agent.published` and `agent.retired`.
- Consumes `instance.*` for auditing and UI refresh.

## Agent API

- `POST /api/v1/agents`: create a new row with `title`, `content (json)`, `activation_code`, and `rate`.
- `GET /api/v1/agents`: list all agents (ordered by `id`).
- `GET /api/v1/agents/{id}`: retrieve a single agent.
- `PATCH /api/v1/agents/{id}`: update any subset of fields.
- `DELETE /api/v1/agents/{id}`: permanently remove an agent.

All routes operate against `shared_psql` using the shared models package. Add validation/tests when fields evolve, and bump `packages/shared_psql_models` accordingly.

## Notes

- Keep RBAC strict—expose admin APIs under `/admin/api/v1/...`.
- All schema changes require Alembic migrations in this service.


