# `event_broker`

## Responsibilities

- Listen to Postgres `NOTIFY` channels for `shared_psql` changes.
- Convert DB events into normalized RabbitMQ messages.
- (Future) Validate incoming REST/event requests before writing to the database.

## Components

- `EventBridge`: manages Postgres + RabbitMQ connections.
- FastAPI endpoints for health, metrics, and manual replays (to be added).
- Imports `shared_psql_models.Base` + models to stay in lockstep with other services when inspecting `shared_psql` payloads.

## Event Rules

- Never publish undocumented routing keys.
- Use idempotency keys when replaying events to avoid duplicates.
- Include `schema_version` on every payload to allow consumer evolution.
- When the shared models package changes, this service must refresh its dependency, update docs, and regenerate migrations if it stores projections.


