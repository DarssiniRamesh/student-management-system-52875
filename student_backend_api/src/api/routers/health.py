from fastapi import APIRouter
from datetime import datetime
from src.schemas.common import BaseResponse

# PUBLIC_INTERFACE
health_router = APIRouter(
    prefix="",
    tags=["Health Check"],
    responses={200: {"description": "Healthy response"}}
)

# PUBLIC_INTERFACE
@health_router.get("/health", summary="Health check endpoint", response_model=BaseResponse)
def health_check():
    """
    Provides a basic backend health/liveness check.
    Returns:
        - success: always true
        - message: server is healthy
        - timestamp: time response was sent
    """
    return BaseResponse(
        success=True,
        message="Backend server is healthy.",
        timestamp=datetime.utcnow(),
    )
