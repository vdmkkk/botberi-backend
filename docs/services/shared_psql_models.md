# `shared_psql_models` Package

Canonical SQLAlchemy + Pydantic definitions for the `shared_psql` database live under `packages/shared_psql_models`. Every service that touches the shared Postgres cluster must use these models to avoid schema drift.

## Responsibilities

- Own the declarative `Base` and naming conventions for constraints.
- Provide reusable SQLAlchemy models (agents, instances, enums) and shared Pydantic schemas for API responses/events.
- Version the shared schema: bump the package version whenever a breaking DB change occurs.

## Usage Pattern

1. Install locally via `pip install -e packages/shared_psql_models`.
2. Import models/metadata inside services:
   ```python
   from shared_psql_models import Base
   from shared_psql_models.models import Agent, Instance
   ```
3. Point Alembic `target_metadata` to `shared_psql_models.Base.metadata` so autogeneration reflects the canonical schema.
4. Re-export/extend Pydantic schemas inside services when additional fields are needed for specific endpoints.

## Change Management Rules

- **Documentation first.** Every edit to this package requires updating:
  - This file (summarize new tables/enums/constraints).
  - `docs/architecture/agents.md` (describe lifecycle or status changes).
  - Any other affected architecture docs (e.g., `event_bus` if payloads change).
- **LLM guidance.** Update `llms.txt` whenever the contribution rules or expectations for this package change. This keeps all coding agents aligned.
- **Migrations.** Regenerate Alembic migrations for *every* service that relies on the updated tables.
- **Versioning.** Increment the version in `packages/shared_psql_models/pyproject.toml` on every breaking change and note the migration requirements in PR descriptions.


