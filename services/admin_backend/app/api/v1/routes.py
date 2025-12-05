from fastapi import APIRouter

from app.api.v1.endpoints import agents, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(agents.router)

__all__ = ["api_router"]


