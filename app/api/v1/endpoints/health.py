from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    timestamp: datetime


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check"""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )