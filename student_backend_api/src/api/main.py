from fastapi import FastAPI
from src.api.routers import auth
from src.api.router_registry import register_all_routers

app = FastAPI(
    title="Student Management Backend API",
    description="Backend API for student management system with admin configuration capabilities.",
    version="1.0.0"
)

# Register all routers, including authentication
register_all_routers(app)
app.include_router(auth.router)
