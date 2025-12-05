import asyncio
import json
from typing import Any

import aio_pika
from app.core.config import get_settings

settings = get_settings()


class EventPublisher:
    def __init__(self) -> None:
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.Channel | None = None
        self._lock = asyncio.Lock()

    async def _ensure_channel(self) -> aio_pika.Channel | None:
        if not settings.event_emit_enabled:
            return None
        async with self._lock:
            if self._channel and not self._channel.is_closed:
                return self._channel
            self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self._channel = await self._connection.channel()
            await self._channel.declare_exchange(
                settings.event_exchange, aio_pika.ExchangeType.TOPIC, durable=True
            )
            return self._channel

    async def publish(self, routing_key: str, payload: dict[str, Any]) -> None:
        channel = await self._ensure_channel()
        if not channel:
            return
        exchange = await channel.get_exchange(settings.event_exchange)
        message = aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )
        await exchange.publish(message, routing_key=routing_key)


publisher = EventPublisher()


async def emit_event(routing_key: str, payload: dict[str, Any]) -> None:
    try:
        await publisher.publish(routing_key, payload)
    except Exception as exc:  # pragma: no cover - logging only
        print(f"[event_bus] failed to publish {routing_key}: {exc}")


__all__ = ["emit_event"]


