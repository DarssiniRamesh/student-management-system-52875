"""
Application configuration and settings management.
"""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application settings
    app_name: str = Field(default="Student Management API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database settings
    database_url: str = Field(
        default="sqlite:///./student_management.db",
        description="Database connection URL"
    )
    
    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, 
        description="Access token expiration time in minutes"
    )
    
    # CORS settings
    allowed_origins: list = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    # Pagination settings
    default_page_size: int = Field(default=20, description="Default pagination size")
    max_page_size: int = Field(default=100, description="Maximum pagination size")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
