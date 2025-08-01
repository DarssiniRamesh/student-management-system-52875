"""
API routers package.
"""
from .config import router as config_router
from .analytics import router as analytics_router

__all__ = ["config_router", "analytics_router"]
