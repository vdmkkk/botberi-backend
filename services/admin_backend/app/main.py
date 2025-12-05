from fastapi import FastAPI

from app.api.v1.routes import api_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title="Botberi Admin Backend",
    version="0.1.0",
    description="Admin/control plane API for managing agents.",
)


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(api_router, prefix=settings.api_v1_prefix)


