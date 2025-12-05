from fastapi import APIRouter

from app.schemas.health import HealthResponse


router = APIRouter()


@router.get("", response_model=HealthResponse, summary="Service readiness probe")
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", detail="admin_backend alive")


