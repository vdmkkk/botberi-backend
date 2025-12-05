# shared-psql-models

Canonical SQLAlchemy + Pydantic definitions for the Botberi `shared_psql` database.

## Why this exists

- `user_backend`, `admin_backend`, `event_broker`, and future services all touch the same `shared_psql` tables.
- Divergent ORM models create schema drift and migration conflicts.
- This package keeps models, metadata, and shared enums in one place so every service stays in sync.

## Usage (local development)

```powershell
pip install -e packages/shared_psql_models
```

Then, in a service:

```python
from shared_psql_models import Base
from shared_psql_models.models import Agent, Instance
```

- Alembic env scripts should import `Base.metadata` when autogenerating migrations.
- Services can build additional Pydantic response models on top of the shared schemas when they need different projections.

## Contribution rules

1. Update `docs/services/shared_psql_models.md` and any affected architecture docs when you add/modify models.
2. Bump the package version here when schema-breaking changes occur.
3. Regenerate Alembic migrations for every service that depends on the changed tables.
4. Update `llms.txt` if the contribution guidelines for this package change.


