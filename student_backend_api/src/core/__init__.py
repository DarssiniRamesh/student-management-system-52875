"""
Core package containing configuration, database, and utility modules.
"""
from .config import settings
from .database import get_db, create_tables

__all__ = ["settings", "get_db", "create_tables"]
