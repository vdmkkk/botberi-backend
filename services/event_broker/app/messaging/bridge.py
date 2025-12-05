import asyncio
import json
from typing import Any

import aio_pika
import asyncpg
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings


class EventBridge:
    """Coordinates Postgres NOTIFY/LISTEN with RabbitMQ publishing."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._pg_conn: asyncpg.Connection | None = None
        self._rmq_conn: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.Channel | None = None
        self._listen_task: asyncio.Task[Any] | None = None

    async def connect(self) -> None:
        """Establish DB + broker connections."""
        pg_dsn = self._settings.database_url.replace("postgresql+asyncpg", "postgresql", 1)
        self._pg_conn = await asyncpg.connect(pg_dsn)
        self._rmq_conn = await aio_pika.connect_robust(self._settings.rabbitmq_url)
        self._channel = await self._rmq_conn.channel()
        await self._pg_conn.add_listener(self._settings.listen_channel, self._handle_notification)
        self._listen_task = asyncio.create_task(self._idle_ping(), name="bridge-ping")

    async def disconnect(self) -> None:
        if self._listen_task:
            self._listen_task.cancel()
        if self._pg_conn:
            await self._pg_conn.close()
        if self._channel:
            await self._channel.close()
        if self._rmq_conn:
            await self._rmq_conn.close()

    async def _idle_ping(self) -> None:
        """Keeps the event loop alive while waiting for NOTIFY callbacks."""
        while True:
            await asyncio.sleep(3600)

    async def _handle_notification(self, *_: Any, payload: str) -> None:  # pragma: no cover - io heavy
        if not self._channel:
            return
        await self._publish(payload)

    async def _publish(self, payload: str) -> None:
        assert self._channel is not None

        routing_key, message_body = self._prepare_message(payload)
        if routing_key is None or message_body is None:
            return

        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(Exception),
            wait=wait_exponential(multiplier=0.2, min=0.5, max=5),
            stop=stop_after_attempt(3),
        ):
            with attempt:
                exchange = await self._channel.declare_exchange(
                    self._settings.outgoing_exchange, aio_pika.ExchangeType.TOPIC
                )
                await exchange.publish(
                    aio_pika.Message(
                        body=message_body,
                        content_type="application/json",
                    ),
                    routing_key=routing_key,
                )

    def _prepare_message(self, payload: str) -> tuple[str | None, bytes | None]:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            print(f"[event_broker] invalid JSON payload: {payload}")
            return None, None

        routing_key = data.get("routing_key")
        if not routing_key:
            print(f"[event_broker] missing routing key in payload: {payload}")
            return None, None

        body = json.dumps(data).encode("utf-8")
        return routing_key, body


