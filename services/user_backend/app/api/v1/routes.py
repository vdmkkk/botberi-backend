from fastapi import APIRouter

from app.api.v1.endpoints import agents, auth, health, instances, users


api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(agents.router)
api_router.include_router(instances.router)

__all__ = ["api_router"]


