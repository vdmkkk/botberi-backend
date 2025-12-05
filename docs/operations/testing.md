# Testing & Tooling

## Commands

```powershell
# Lint + format
ruff check .
ruff format --check .

# Run tests for a service
pushd services/user_backend
pytest
popd
```

## Expectations

- Every bug fix or feature must include at least one test.
- Use `pytest-asyncio` for async FastAPI route tests. Prefer `httpx.AsyncClient` over hitting the network.
- Contract tests for RabbitMQ events should live under `tests/contracts/`.
- Celery tasks (limited to `user_backend` and `admin_backend`) require unit tests that assert retry/backoff policies.
- Favor factories/fixtures instead of manual object creation.

## Coverage

- Target 85%+ statement coverage per service.
- Critical modules (auth, agent lifecycle) should approach 100%.
- Use `pytest --cov=app --cov-report=xml` when adding major features to keep CI ready.

## Linters & Formatters

- `ruff` handles lint + import sorting + formatting. Avoid mixing tools.
- `mypy` will be added later; keep type hints accurate to minimize future work.
