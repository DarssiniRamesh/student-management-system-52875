from fastapi import FastAPI
from src.api.router_registry import register_all_routers

app = FastAPI(
    title="Student Management Backend API",
    description="Backend API for student management system with admin configuration capabilities.",
    version="1.0.0"
)

# PUBLIC_INTERFACE
# Register all routers for the FastAPI backend.
register_all_routers(app)
