"""
Configuration management API endpoints.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.auth import get_current_active_user, get_current_superuser
from ...models.admin import Admin
from ...services.config_service import ConfigService
from ...schemas.config import (
    ConfigCreate, ConfigUpdate, ConfigResponse,
    FeatureToggleCreate, FeatureToggleUpdate, FeatureToggleResponse,
    RuntimeConfigResponse, ConfigBulkUpdate
)
from ...schemas.common import BaseResponse, PaginatedResponse

router = APIRouter(
    prefix="/config",
    tags=["Configuration Management"],
)


def get_config_service(db: Session = Depends(get_db)) -> ConfigService:
    """Dependency to get configuration service."""
    return ConfigService(db)


# Configuration endpoints
@router.get(
    "/configurations",
    response_model=PaginatedResponse[ConfigResponse],
    summary="Get configurations",
    description="Retrieve configurations with optional filtering and pagination. Sensitive configurations are hidden unless explicitly requested by superusers."
)
def get_configurations(
    category: Optional[str] = Query(None, description="Filter by configuration category"),
    include_sensitive: bool = Query(False, description="Include sensitive configurations (superuser only)"),
    include_system: bool = Query(True, description="Include system configurations"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get configurations with filtering and pagination.
    
    - **category**: Filter configurations by category
    - **include_sensitive**: Include sensitive configurations (requires superuser privileges)
    - **include_system**: Include system-level configurations
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (1-100)
    
    Returns paginated list of configurations with metadata.
    """
    # Only superusers can access sensitive configurations
    if include_sensitive and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access sensitive configurations"
        )
    
    configurations, total = config_service.get_configurations(
        category=category,
        include_sensitive=include_sensitive,
        include_system=include_system,
        skip=skip,
        limit=limit
    )
    
    # Calculate pagination metadata
    pages = (total + limit - 1) // limit
    
    return PaginatedResponse[ConfigResponse](
        items=[ConfigResponse.from_orm(config) for config in configurations],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )


@router.get(
    "/configurations/{key}",
    response_model=ConfigResponse,
    summary="Get configuration by key",
    description="Retrieve a specific configuration by its key."
)
def get_configuration(
    key: str,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get a specific configuration by key.
    
    - **key**: Configuration key to retrieve
    
    Returns the configuration if found, otherwise 404.
    """
    # Check if user can access sensitive configs
    include_sensitive = current_user.is_superuser
    
    config = config_service.get_configuration(key, include_sensitive=include_sensitive)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with key '{key}' not found"
        )
    
    return ConfigResponse.from_orm(config)


@router.post(
    "/configurations",
    response_model=ConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create configuration",
    description="Create a new configuration entry."
)
def create_configuration(
    config_data: ConfigCreate,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Create a new configuration.
    
    - **key**: Unique configuration key
    - **value**: Configuration value (can be string, number, boolean, object, or array)
    - **description**: Optional description
    - **category**: Configuration category for grouping
    - **is_sensitive**: Whether the configuration contains sensitive data
    - **is_system**: Whether this is a system-level configuration
    
    Returns the created configuration.
    """
    config = config_service.create_configuration(config_data, current_user.id)
    return ConfigResponse.from_orm(config)


@router.put(
    "/configurations/{key}",
    response_model=ConfigResponse,
    summary="Update configuration",
    description="Update an existing configuration."
)
def update_configuration(
    key: str,
    config_data: ConfigUpdate,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Update an existing configuration.
    
    - **key**: Configuration key to update
    - **value**: New configuration value
    - **description**: Updated description
    - **category**: Updated category
    - **is_sensitive**: Updated sensitivity flag
    
    System configurations can only be updated by superusers.
    """
    allow_system = current_user.is_superuser
    
    config = config_service.update_configuration(
        key, config_data, current_user.id, allow_system=allow_system
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with key '{key}' not found"
        )
    
    return ConfigResponse.from_orm(config)


@router.delete(
    "/configurations/{key}",
    response_model=BaseResponse,
    summary="Delete configuration",
    description="Delete a configuration (soft delete)."
)
def delete_configuration(
    key: str,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Delete a configuration.
    
    - **key**: Configuration key to delete
    
    System configurations can only be deleted by superusers.
    This is a soft delete - the configuration is marked as inactive.
    """
    allow_system = current_user.is_superuser
    
    deleted = config_service.delete_configuration(key, allow_system=allow_system)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with key '{key}' not found"
        )
    
    return BaseResponse(message=f"Configuration '{key}' deleted successfully")


# Feature Toggle endpoints
@router.get(
    "/feature-toggles",
    response_model=PaginatedResponse[FeatureToggleResponse],
    summary="Get feature toggles",
    description="Retrieve feature toggles with optional filtering and pagination."
)
def get_feature_toggles(
    environment: Optional[str] = Query(None, description="Filter by environment"),
    enabled_only: bool = Query(False, description="Only return enabled toggles"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get feature toggles with filtering and pagination.
    
    - **environment**: Filter by environment (all, development, staging, production, test)
    - **enabled_only**: Only return enabled feature toggles
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (1-100)
    
    Returns paginated list of feature toggles.
    """
    toggles, total = config_service.get_feature_toggles(
        environment=environment,
        enabled_only=enabled_only,
        skip=skip,
        limit=limit
    )
    
    # Calculate pagination metadata
    pages = (total + limit - 1) // limit
    
    return PaginatedResponse[FeatureToggleResponse](
        items=[FeatureToggleResponse.from_orm(toggle) for toggle in toggles],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )


@router.get(
    "/feature-toggles/{name}",
    response_model=FeatureToggleResponse,
    summary="Get feature toggle by name",
    description="Retrieve a specific feature toggle by its name."
)
def get_feature_toggle(
    name: str,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get a specific feature toggle by name.
    
    - **name**: Feature toggle name to retrieve
    
    Returns the feature toggle if found, otherwise 404.
    """
    toggle = config_service.get_feature_toggle(name)
    if not toggle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature toggle with name '{name}' not found"
        )
    
    return FeatureToggleResponse.from_orm(toggle)


@router.post(
    "/feature-toggles",
    response_model=FeatureToggleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create feature toggle",
    description="Create a new feature toggle."
)
def create_feature_toggle(
    toggle_data: FeatureToggleCreate,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Create a new feature toggle.
    
    - **name**: Unique feature name
    - **enabled**: Whether the feature is enabled
    - **description**: Optional description
    - **environment**: Environment where toggle applies
    - **rollout_percentage**: Percentage rollout (0-100)
    - **user_groups**: List of user groups with access
    - **conditions**: Additional conditions for activation
    
    Returns the created feature toggle.
    """
    toggle = config_service.create_feature_toggle(toggle_data, current_user.id)
    return FeatureToggleResponse.from_orm(toggle)


@router.put(
    "/feature-toggles/{name}",
    response_model=FeatureToggleResponse,
    summary="Update feature toggle",
    description="Update an existing feature toggle."
)
def update_feature_toggle(
    name: str,
    toggle_data: FeatureToggleUpdate,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Update an existing feature toggle.
    
    - **name**: Feature toggle name to update
    - **enabled**: Updated enabled state
    - **description**: Updated description
    - **environment**: Updated environment
    - **rollout_percentage**: Updated rollout percentage
    - **user_groups**: Updated user groups
    - **conditions**: Updated conditions
    
    Returns the updated feature toggle.
    """
    toggle = config_service.update_feature_toggle(name, toggle_data, current_user.id)
    
    if not toggle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature toggle with name '{name}' not found"
        )
    
    return FeatureToggleResponse.from_orm(toggle)


@router.delete(
    "/feature-toggles/{name}",
    response_model=BaseResponse,
    summary="Delete feature toggle",
    description="Delete a feature toggle (soft delete)."
)
def delete_feature_toggle(
    name: str,
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Delete a feature toggle.
    
    - **name**: Feature toggle name to delete
    
    This is a soft delete - the toggle is marked as inactive.
    """
    deleted = config_service.delete_feature_toggle(name)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature toggle with name '{name}' not found"
        )
    
    return BaseResponse(message=f"Feature toggle '{name}' deleted successfully")


# Runtime configuration endpoints
@router.get(
    "/runtime",
    response_model=RuntimeConfigResponse,
    summary="Get runtime configuration",
    description="Get current runtime configuration including all active settings and feature toggles."
)
def get_runtime_config(
    environment: str = Query("all", description="Environment to get config for"),
    include_sensitive: bool = Query(False, description="Include sensitive configurations (superuser only)"),
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get runtime configuration for the application.
    
    - **environment**: Environment to get configuration for
    - **include_sensitive**: Include sensitive configurations (requires superuser)
    
    Returns current runtime configuration including:
    - All active configurations
    - All active feature toggles
    - Metadata about the configuration state
    """
    # Only superusers can access sensitive configurations
    if include_sensitive and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can access sensitive configurations"
        )
    
    return config_service.get_runtime_config(
        environment=environment,
        include_sensitive=include_sensitive
    )


@router.get(
    "/feature-check/{feature_name}",
    response_model=Dict[str, Any],
    summary="Check if feature is enabled",
    description="Check if a specific feature is enabled for the current user/context."
)
def check_feature_enabled(
    feature_name: str,
    environment: str = Query("all", description="Environment context"),
    user_id: Optional[str] = Query(None, description="User ID to check for"),
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Check if a feature is enabled.
    
    - **feature_name**: Name of the feature to check
    - **environment**: Environment context
    - **user_id**: Optional user ID to check rollout for
    
    Returns whether the feature is enabled and additional metadata.
    """
    # Use admin's groups if available
    user_groups = ["admin"] if current_user.is_admin else []
    if current_user.is_superuser:
        user_groups.append("superuser")
    
    enabled = config_service.is_feature_enabled(
        feature_name=feature_name,
        user_id=user_id or str(current_user.id),
        user_groups=user_groups,
        environment=environment
    )
    
    return {
        "feature_name": feature_name,
        "enabled": enabled,
        "environment": environment,
        "checked_for_user": user_id or str(current_user.id),
        "user_groups": user_groups
    }


# Utility endpoints
@router.get(
    "/categories",
    response_model=List[str],
    summary="Get configuration categories",
    description="Get all unique configuration categories."
)
def get_config_categories(
    current_user: Admin = Depends(get_current_active_user),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Get all unique configuration categories.
    
    Returns list of category names used in configurations.
    """
    return config_service.get_categories()


@router.post(
    "/bulk-update",
    response_model=Dict[str, Any],
    summary="Bulk update configurations",
    description="Update multiple configurations in a single request (superuser only)."
)
def bulk_update_configs(
    bulk_data: ConfigBulkUpdate,
    current_user: Admin = Depends(get_current_superuser),
    config_service: ConfigService = Depends(get_config_service)
):
    """
    Bulk update multiple configurations.
    
    Requires superuser privileges. Updates existing configurations
    and creates new ones as needed.
    
    Returns summary of the bulk update operation.
    """
    results = config_service.bulk_update_configs(
        bulk_data.configurations,
        current_user.id
    )
    
    return {
        "summary": results,
        "updated_by": current_user.username,
        "timestamp": datetime.utcnow()
    }
