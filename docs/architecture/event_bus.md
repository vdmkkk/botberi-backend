# Event Bus Contracts

RabbitMQ (`event_bus`) is the canonical channel for cross-service communication. Every event must be documented here before implementation.

## Exchanges & Queues

| Exchange        | Type   | Purpose                               |
| --------------- | ------ | ------------------------------------- |
| `events.topic`  | topic  | Default exchange for domain events.   |
| `agents.direct` | direct | Agent/instance control plane fan-out. |

| Queue                     | Bound Exchange | Routing Keys                           | Consumers       |
| ------------------------- | -------------- | -------------------------------------- | --------------- |
| `agents_worker.instance`  | `events.topic` | `instance.*`                           | `agents_worker` |
| `user_backend.ws_updates` | `events.topic` | `instance.updated`, `instance.deleted` | `user_backend`  |
| `admin_backend.audit`     | `events.topic` | `agent.*`, `instance.*`                | `admin_backend` |

## Event Catalog

### `instance.created`

- **Routing key:** `instance.created`
- **Published by:** `event_broker` after `shared_psql` insert / API create.
- **Payload:**
  ```json
  {
    "instance_id": "<uuid>",
    "agent_id": "<uuid>",
    "user_id": "<uuid>",
    "config": { "...": "..." },
    "created_at": "2025-01-01T12:00:00Z",
    "status": "pending"
  }
  ```
- **Consumers:** `agents_worker`, `admin_backend` (audit).
- **Side effects:** Kick off agent pipeline.

### `instance.updated`

- **Routing key:** `instance.updated`
- **Published by:** `event_broker` when `shared_psql` row changes.
- **Payload fields:**
  - `instance_id`
  - `status` (enum: `pending`, `running`, `failed`, `stopped`)
  - `metadata` (optional)
  - `updated_at`
- **Consumers:** `user_backend` (push via WS), `admin_backend`.

### `instance.deleted`

- **Routing key:** `instance.deleted`
- **Published by:** `user_backend` API delete -> `event_broker`.
- **Consumers:** `agents_worker` (cleanup), `admin_backend`.

### `agent.published`

- **Routing key:** `agent.published`
- **Published by:** `admin_backend` when an agent becomes available.
- **Payload:** `agent_id`, `name`, `version`, `capabilities`.
- **Consumers:** `user_backend` (refresh catalog), `agents_worker`.

### `agent.retired`

- **Routing key:** `agent.retired`
- **Purpose:** inform services to stop new instances for a given agent.

## Postgres NOTIFY Bridge

- `shared_psql` triggers:
  - `instances_notify`: emits JSON payloads describing insert/update/delete events.
  - The payload includes `event_type`, `table`, and `row_data`.
- `event_broker` listens via async connection, translates the payload into RabbitMQ events listed above.
- All schemas emitted by triggers must be versioned; bump the `schema_version` field when breaking changes occur.

## Change Process

1. Update this file with the new/changed event.
2. Open an architecture discussion if the change affects routing rules.
3. Implement publisher + consumer code paths with contract tests.
4. Update `llms.txt` if the new workflow introduces global rules (e.g., new mandatory headers).
