from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.config import router as config_router
from .routers.analytics import router as analytics_router
from ..core.config import settings
from ..core.database import create_tables

app = FastAPI(
    title="Student Management Backend API",
    description="Backend API for student management system with admin configuration capabilities. Includes analytics and dashboard metrics for admin/operator consumption.",
    version=settings.app_version,
    openapi_tags=[
        {
            "name": "Configuration Management",
            "description": "Dynamic configuration and feature toggle management endpoints"
        },
        {
            "name": "Admin Analytics & Dashboard",
            "description": "System metrics and dashboard analytics for operator/admin consumption"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(config_router, prefix="/api/v1")
app.include_router(analytics_router)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    create_tables()

@app.get("/")
def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Health status message
    """
    return {
        "message": "Healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "operational"
    }

@app.get("/health")
def detailed_health_check():
    """
    Detailed health check endpoint with system information.
    
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
