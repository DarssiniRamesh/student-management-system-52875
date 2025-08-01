"""
Router registry for dynamic plug-and-play API router inclusion.

To enable plug-and-play extension, additional routers can be registered here
through the centralized list, and then auto-included by the application.
"""

from typing import List, Tuple, Optional
from fastapi import APIRouter

RouterEntry = Tuple[APIRouter, Optional[str], Optional[str]]  # (router, prefix, tags)
from fastapi import FastAPI

class RouterRegistry:
    """
    Plug-and-play registry for API routers.

    - Register routers and their prefixes/tags here for dynamic inclusion.
    - New routers can be appended here without modifying app logic.
    """
    _registry: List[RouterEntry] = []

    @classmethod
    # PUBLIC_INTERFACE
    def register(cls, router: APIRouter, prefix: Optional[str] = None, tags: Optional[str] = None):
        """
        Register a router with an optional prefix and custom tags.

        Args:
            router (APIRouter): FastAPI router instance.
            prefix (str): Route prefix.
            tags (str): Tags for OpenAPI docs.
        """
        cls._registry.append((router, prefix, tags))

    @classmethod
    # PUBLIC_INTERFACE
    def get_routes(cls) -> List[RouterEntry]:
        """Retrieve all registered routers (in order)."""
        return cls._registry


# Example usage:
# from .routers.config import router as config_router
# RouterRegistry.register(config_router, prefix="/api/v1")

from .routers.config import router as config_router
from .routers.analytics import analytics_router
from .routers.auth import router as auth_router

# Register routers here for plug-and-play extensibility
RouterRegistry.register(config_router, prefix="/api/v1/config", tags="Configuration Management")
RouterRegistry.register(analytics_router, prefix="/admin/analytics", tags="Admin Analytics & Dashboard")
RouterRegistry.register(auth_router, prefix="/api/v1/auth", tags="Authentication")

# PUBLIC_INTERFACE
def register_all_routers(app: FastAPI):
    """
    Register all routers in the RouterRegistry with the FastAPI app.

    Args:
        app (FastAPI): FastAPI application instance.
    """
    for router, prefix, tags in RouterRegistry.get_routes():
        include_kwargs = {}
        if prefix:
            include_kwargs["prefix"] = prefix
        if tags:
            include_kwargs["tags"] = [tags] if isinstance(tags, str) else tags
        app.include_router(router, **include_kwargs)
