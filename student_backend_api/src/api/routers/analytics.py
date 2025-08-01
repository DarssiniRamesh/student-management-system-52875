"""
Analytics and dashboard metrics API endpoints for admin use.

This router exposes protected endpoints under /admin/analytics for system and database stats, usage analytics, and API metrics, intended for admin dashboard consumption.

All endpoints require admin authentication.
"""
from datetime import datetime, timedelta
import time
import platform
import os
import psutil
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.auth import get_current_superuser
from ...models.student import Student
from ...models.admin import Admin
from ...models.config import Configuration, FeatureToggle

router = APIRouter(
    prefix="/admin/analytics",
    tags=["Admin Analytics & Dashboard"],
)

_START_TIME = time.time()


def get_uptime_seconds() -> int:
    """Calculate application uptime in seconds."""
    return int(time.time() - _START_TIME)


def get_system_info():
    """Get host system info."""
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu_cores": os.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
        "boot_time": datetime.utcfromtimestamp(psutil.boot_time()).isoformat() + "Z"
    }


# PUBLIC_INTERFACE
@router.get(
    "/metrics",
    summary="Get system and application metrics",
    description="Return runtime system/application metrics for dashboard/analytics. For admin only.",
    response_model=dict,
    responses={
        200: {"description": "System/application metrics in JSON schema."},
        401: {"description": "Unauthorized access."}
    }
)
def get_metrics(current_user: Admin = Depends(get_current_superuser)):
    """
    Fetch system and application metrics such as uptime, current server time, host info, and resource usage.
    Only available to authenticated superusers/admins.

    Returns:
        dict: System and application metrics.
    """
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss
    cpu = process.cpu_percent(interval=0.2)
    disk = psutil.disk_usage('/')

    return {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": get_uptime_seconds(),
        "system": get_system_info(),
        "resource_usage": {
            "cpu_percent": cpu,
            "ram_mb": int(mem / 1024 / 1024),
            "virtual_memory_percent": psutil.virtual_memory().percent,
            "disk_percent": disk.percent,
        },
        "process_id": os.getpid(),
    }


# PUBLIC_INTERFACE
@router.get(
    "/db-stats",
    summary="Get database statistics and usage counts",
    description="Return current database stats including student, admin, config, and feature toggle counts.",
    response_model=dict,
    responses={
        200: {"description": "Database stats as JSON."},
        401: {"description": "Unauthorized"}
    }
)
def db_stats(current_user: Admin = Depends(get_current_superuser), db: Session = Depends(get_db)):
    """
    Return record counts and basic DB info for main tables.
    Only admin/superuser can fetch.

    Returns:
        dict: Record counts for entities, last updated timestamps, etc.
    """
    student_count = db.query(Student).filter(Student.is_active == True).count()
    admin_count = db.query(Admin).filter(Admin.is_active == True).count()
    config_count = db.query(Configuration).filter(Configuration.is_active == True).count()
    toggle_count = db.query(FeatureToggle).filter(FeatureToggle.is_active == True).count()

    latest_student = db.query(Student).order_by(Student.updated_at.desc()).first()
    latest_admin = db.query(Admin).order_by(Admin.updated_at.desc()).first()

    return {
        "totals": {
            "students": student_count,
            "active_admins": admin_count,
            "active_configurations": config_count,
            "active_feature_toggles": toggle_count,
        },
        "latest_update": {
            "student": latest_student.updated_at.isoformat() + "Z" if latest_student else None,
            "admin": latest_admin.updated_at.isoformat() + "Z" if latest_admin else None
        }
    }


# PUBLIC_INTERFACE
@router.get(
    "/api-usage",
    summary="Get API usage dummy metrics",
    description="Return summary data on API usage such as request counts, error rates (currently dummy, future: log-based).",
    response_model=dict,
    responses={
        200: {"description": "API usage statistics (sample/dummy data)."},
        401: {"description": "Unauthorized"}
    }
)
def api_usage(current_user: Admin = Depends(get_current_superuser)):
    """
    Return API usage analytics for the dashboard.
    For now, serve sample/dummy data; future: implement middleware/log parsing for detailed analytics.

    Returns:
        dict: API usage summary (requests, errors, types).
    """
    # TODO: Replace with real usage from logs or tracking
    return {
        "api_usage": {
            "total_requests": 2345,
            "successful_requests": 2255,
            "error_requests": 90,
            "requests_per_endpoint": {
                "/api/v1/config/configurations": 520,
                "/api/v1/config/feature-toggles": 320,
                "/admin/analytics/metrics": 25
            },
            "errors_last_24h": [
                {"timestamp": "2024-06-18T12:03:27Z", "endpoint": "/api/v1/config/configurations", "status_code": 500, "details": "DBTimeout"},
                {"timestamp": "2024-06-18T15:22:11Z", "endpoint": "/api/v1/config/configurations", "status_code": 403, "details": "Forbidden"},
            ]
        },
        "metrics_generated_at": datetime.utcnow().isoformat() + "Z"
    }

# PUBLIC_INTERFACE
@router.get(
    "/uptime",
    summary="Get server uptime",
    description="Returns how long the backend has been running.",
    response_model=dict,
    responses={
        200: {"description": "Uptime in seconds and readable format."}
    }
)
def get_uptime(current_user: Admin = Depends(get_current_superuser)):
    """
    Returns uptime in seconds and a human-readable format.

    Returns:
        dict: uptime_seconds and uptime_human
    """
    total_seconds = get_uptime_seconds()
    human = str(timedelta(seconds=total_seconds))
    return {
        "uptime_seconds": total_seconds,
        "uptime": human
    }

# PUBLIC_INTERFACE
@router.get(
    "/errors",
    summary="Get recent error logs (placeholder)",
    description="Returns a summary of recent errors - currently stubbed, designed for future integration.",
    response_model=dict,
    responses={200: {"description": "Error events."}}
)
def get_errors(current_user: Admin = Depends(get_current_superuser)):
    """
    Returns a summary of recent system errors (to be implemented with real log backend).

    Returns:
        dict: List of errors
    """
    # TODO: integrate with real log/error system
    return {
        "errors": [
            {"timestamp": "2024-06-18T15:23:52Z", "error_type": "DatabaseError", "details": "Connection timed out."},
            {"timestamp": "2024-06-16T19:01:31Z", "error_type": "ValidationError", "details": "Configuration key missing."}
        ],
        "note": "Stub data; integrate with logging for production."
    }

