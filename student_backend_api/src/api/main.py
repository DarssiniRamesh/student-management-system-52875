from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from ..core.config import settings
from ..core.database import create_tables

from .router_registry import RouterRegistry

# Import and register built-in routers:
from .routers.config import router as config_router
from .routers.analytics import router as analytics_router

RouterRegistry.register(config_router, prefix="/api/v1", tags=["Configuration Management"])
RouterRegistry.register(analytics_router, prefix=None, tags=["Admin Analytics & Dashboard"])

# OpenAPI metadata
OPENAPI_TITLE = os.getenv("OPENAPI_TITLE", "Student Management Backend API")
OPENAPI_DESCRIPTION = os.getenv("OPENAPI_DESCRIPTION",
    "Backend API for student management system with admin configuration capabilities. Includes analytics and dashboard metrics for admin/operator consumption."
)
OPENAPI_VERSION = settings.app_version
OPENAPI_CONTACT = {
    "name": "School DevOps Team",
    "email": "admin@example.com",
    "url": "https://yourdomain.example"
}
OPENAPI_LICENSE = {
    "name": "MIT",
    "url": "https://opensource.org/licenses/MIT"
}
OPENAPI_TAGS = [
    {
        "name": "Configuration Management",
        "description": "Dynamic configuration and feature toggle management endpoints"
    },
    {
        "name": "Admin Analytics & Dashboard",
        "description": "System metrics and dashboard analytics for operator/admin consumption"
    },
    {
        "name": "Health",
        "description": "API health and diagnostics"
    }
]

OPENAPI_CUSTOM_METADATA = {
    "x-api-group": "student-management",
    "x-plug-and-play": True,
    "x-support-contact": "support@yourdomain.example"
}

app = FastAPI(
    title=OPENAPI_TITLE,
    description=OPENAPI_DESCRIPTION,
    version=OPENAPI_VERSION,
    contact=OPENAPI_CONTACT,
    license_info=OPENAPI_LICENSE,
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global CORS config, supports env override for allowed origins (comma-separated)
def get_cors_allowed_origins():
    origins_env = os.getenv("CORS_ALLOWED_ORIGINS")
    if origins_env:
        return [o.strip() for o in origins_env.split(",")]
    return settings.allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamically include all routers from registry (plug-and-play!)
for _router, _prefix, _tags in RouterRegistry.get_routes():
    app.include_router(_router, prefix=_prefix or "", tags=_tags if _tags else None)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    create_tables()

# PUBLIC_INTERFACE
@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify API is running.
    ---
    Returns:
        dict: Health status message
    """
    return {
        "message": "Healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "operational"
    }

# PUBLIC_INTERFACE
@app.get("/health", tags=["Health"])
def detailed_health_check():
    """
    Detailed health check endpoint with system information.
    ---
    Returns:
        dict: Detailed health status and system info
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug_mode": settings.debug,
        "environment": "development" if settings.debug else "production",
        "features": {
            "configuration_management": True,
            "feature_toggles": True,
            "admin_authentication": True
        }
    }

# PUBLIC_INTERFACE
@app.get("/openapi-metadata", tags=["Health"])
def openapi_metadata():
    """
    Get custom OpenAPI metadata and extensions for plug-and-play introspection.
    ---
    Returns:
        dict: Custom OpenAPI info/metadata (x-prefixed fields)
    """
    return OPENAPI_CUSTOM_METADATA

# Optionally attach OpenAPI custom metadata as doc extension for /openapi.json
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    # Inject our custom metadata keys for discovery
    openapi_schema.update(OPENAPI_CUSTOM_METADATA)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

