from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from src.api.router_registry import register_all_routers

app = FastAPI(
    title="Student Management Backend API",
    description="Backend API for student management system with admin configuration capabilities.",
    version="1.0.0"
)

# PUBLIC_INTERFACE
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Ensures that all Pydantic validation errors (including extra field rejection) are handled with a standard 422 format, never escalated to 500.
    Returns FastAPI's standard validation error response.
    """
    return await request_validation_exception_handler(request, exc)

# PUBLIC_INTERFACE
# Register all routers for the FastAPI backend.
register_all_routers(app)
