from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routes import api_router
from app.core.config import get_settings
from app.messaging.bridge import EventBridge


settings = get_settings()
bridge = EventBridge(settings=settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await bridge.connect()
    yield
    await bridge.disconnect()


app = FastAPI(
    title="Botberi Event Broker",
    version="0.1.0",
    description="Bridges Postgres NOTIFY and RabbitMQ events.",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


