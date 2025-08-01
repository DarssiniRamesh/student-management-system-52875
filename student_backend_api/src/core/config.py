import os

class Settings:
    # SECURITY and JWT config vars
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # PUBLIC_INTERFACE
    @property
    def database_url(self) -> str:
        """
        Returns the database connection URL.
        Reads from DATABASE_URL environment variable.
        Defaults to a local SQLite file for dev if not set, but errors on true production.
        """
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            return db_url
        # Fallback: use a local SQLite file (for dev) and warn
        fallback_sqlite = "sqlite:///./dev.db"
        if os.getenv("ENV", "development") == "production":
            raise RuntimeError("DATABASE_URL environment variable is not set! Aborting startup.")
        print("[WARNING] DATABASE_URL not set, using default local SQLite database ./dev.db.")
        return fallback_sqlite

settings = Settings()
