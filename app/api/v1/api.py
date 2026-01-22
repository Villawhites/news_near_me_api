from fastapi import APIRouter
from app.api.v1.endpoints.news import router as news_router
from app.api.v1.endpoints.health import router as health_router

api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    news_router,
    prefix="/news",
    tags=["News"]
)