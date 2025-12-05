from fastapi import APIRouter

from app.api.v1 import endpoints


api_router = APIRouter()
api_router.include_router(endpoints.health.router, prefix="/health", tags=["health"])

__all__ = ["api_router"]


