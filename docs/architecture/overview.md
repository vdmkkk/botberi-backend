# Architecture Overview

## Service Boundaries

| Domain              | Owner Service                    | Data Store                 | Purpose                                                               |
| ------------------- | -------------------------------- | -------------------------- | --------------------------------------------------------------------- |
| Identity & auth     | `user_backend`                   | `user_psql`                | Account lifecycle, sessions, API keys.                                |
| Agent catalog       | `admin_backend`                  | `shared_psql`              | Curate available agents and templates.                                |
| Instance runtime    | `user_backend` + `agents_worker` | `shared_psql`              | Create/manage agent instances; `agents_worker` executes ML workflows. |
| Event orchestration | `event_broker`                   | RabbitMQ + Postgres NOTIFY | Normalize DB change events and publish/consume RabbitMQ messages.     |

### Event Flow Snapshot

1. `user_backend` writes an instance row to `shared_psql`.
2. Postgres `NOTIFY` triggers `event_broker`.
3. `event_broker` publishes `instance.created` to RabbitMQ (`event_bus`).
4. `agents_worker` consumes the event, kicks off ML pipelines, updates status in `shared_psql`.
5. `event_broker` pushes `instance.updated` to RabbitMQ and WebSocket channels, so `user_backend` can fan it out to frontends in real time.

## Networking

- Internal traffic is routed through the Docker network `botberi_net`.
- `nginx` (port `8080` outside, `80` inside) terminates TLS (to be added) and proxies REST + WebSockets to the proper backend.
- Each backend exposes auto-generated Swagger at `/docs`.

## Observability

- Flower (`:4400`) provides live Celery worker/queue stats exclusively for `user_backend` and `admin_backend`.
- RabbitMQ Management (`:15672`) shows broker metrics.
- Grafana container is provisioned (see `infra/grafana/`) for future dashboards (Celery, Postgres, custom app metrics). Datasources hook into Prometheus/Flower HTTP APIs.

## Shared Schema Package

- `packages/shared_psql_models` contains the authoritative SQLAlchemy models + Pydantic schemas for anything stored in `shared_psql`.
- Every service that touches shared data must import from this package; never duplicate models locally.
- Edits to the package require updating `docs/services/shared_psql_models.md`, the relevant architecture docs, and `llms.txt`, plus fresh Alembic migrations across affected services.

## Scaling Strategy

- Each backend runs stateless containers; scale horizontally by increasing replicas in Compose/Swarm/Kubernetes.
- Only `user_backend` and `admin_backend` own Celery workers; scale their queues independently as load grows, while other services rely on HTTP + RabbitMQ flows.
- Postgres instances mount volumes under `docker-data/` to preserve dev state. Use managed Postgres in prod.
- Event bus (RabbitMQ) should be deployed in clustered HA mode for prod; Compose keeps a single node for dev.

## Directory Map

```
docs/
  architecture/      # high-level diagrams, contracts
  operations/        # runbooks, testing instructions
env/
  dev|prod/          # env templates for Compose + services
infra/
  grafana/           # provisioning + dashboards
  nginx/             # routing config
services/
  user_backend/
  admin_backend/
  event_broker/
```

Update this file whenever the service graph changes.
