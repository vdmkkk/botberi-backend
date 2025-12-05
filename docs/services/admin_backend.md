# `admin_backend`

## Responsibilities

- Manage the catalog of publishable agents (draft, review, publish, retire).
- Audit trail for agent and instance changes.
- Administrative dashboards and tooling for support teams.
- Owns the admin-facing Celery queue (monitored via Flower alongside `user_backend`) for long-running review workflows.

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

## Notes

- Keep RBAC strict—expose admin APIs under `/admin/api/v1/...`.
- All schema changes require Alembic migrations in this service.


