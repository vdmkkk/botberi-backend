from fastapi import FastAPI

from app.api.v1.routes import api_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title="Botberi User Backend",
    version="0.1.0",
    description="User-facing API for authentication, agent catalog, and instance lifecycle.",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/healthz", tags=["health"])
async def runtime_health() -> dict[str, str]:
    """Basic container health endpoint used by Kubernetes/Compose."""
    return {"status": "ok", "service": settings.app_name}


app.include_router(api_router, prefix=settings.api_v1_prefix)


