"""
Configuration-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator




class ConfigBase(BaseModel):
    """Base configuration schema with common fields."""
    key: str = Field(..., min_length=1, max_length=255, description="Configuration key")
    value: Union[str, int, float, bool, dict, list] = Field(..., description="Configuration value")
    description: Optional[str] = Field(None, description="Description of the configuration")
    category: str = Field(..., min_length=1, max_length=100, description="Configuration category")
    is_sensitive: bool = Field(False, description="Whether the configuration is sensitive")
    is_system: bool = Field(False, description="Whether the configuration is system-level")

    @validator('key')
    def validate_key(cls, v):
        # Only allow alphanumeric, dots, underscores, and hyphens
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Key must contain only alphanumeric characters, dots, underscores, and hyphens')
        return v


class ConfigCreate(ConfigBase):
    """Schema for creating a new configuration."""
    pass


class ConfigUpdate(BaseModel):
    """Schema for updating configuration."""
    value: Optional[Union[str, int, float, bool, dict, list]] = None
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    is_sensitive: Optional[bool] = None


class ConfigResponse(ConfigBase):
    """Schema for configuration response."""
    id: int = Field(..., description="Internal database ID")
    created_at: datetime = Field(..., description="When the configuration was created")
    updated_at: datetime = Field(..., description="When the configuration was last updated")
    is_active: bool = Field(..., description="Whether the configuration is active")
    created_by: Optional[int] = Field(None, description="ID of admin who created this config")
    updated_by: Optional[int] = Field(None, description="ID of admin who last updated this config")

    class Config:
        from_attributes = True


class FeatureToggleBase(BaseModel):
    """Base feature toggle schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Feature name")
    enabled: bool = Field(False, description="Whether the feature is enabled")
    description: Optional[str] = Field(None, description="Description of the feature")
    environment: str = Field("all", max_length=50, description="Environment where feature applies")
    rollout_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Rollout percentage (0-100)")
    user_groups: List[str] = Field(default_factory=list, description="User groups that have access")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Additional conditions")

    @validator('name')
    def validate_name(cls, v):
        # Only allow alphanumeric, dots, underscores, and hyphens
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Feature name must contain only alphanumeric characters, dots, underscores, and hyphens')
        return v

    @validator('environment')
    def validate_environment(cls, v):
        allowed_envs = ['all', 'development', 'staging', 'production', 'test']
        if v not in allowed_envs:
            raise ValueError(f'Environment must be one of: {", ".join(allowed_envs)}')
        return v


class FeatureToggleCreate(FeatureToggleBase):
    """Schema for creating a new feature toggle."""
    pass


class FeatureToggleUpdate(BaseModel):
    """Schema for updating feature toggle."""
    enabled: Optional[bool] = None
    description: Optional[str] = None
    environment: Optional[str] = Field(None, max_length=50)
    rollout_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    user_groups: Optional[List[str]] = None
    conditions: Optional[Dict[str, Any]] = None

    @validator('environment')
    def validate_environment(cls, v):
        if v is not None:
            allowed_envs = ['all', 'development', 'staging', 'production', 'test']
            if v not in allowed_envs:
                raise ValueError(f'Environment must be one of: {", ".join(allowed_envs)}')
        return v


class FeatureToggleResponse(FeatureToggleBase):
    """Schema for feature toggle response."""
    id: int = Field(..., description="Internal database ID")
    created_at: datetime = Field(..., description="When the feature toggle was created")
    updated_at: datetime = Field(..., description="When the feature toggle was last updated")
    is_active: bool = Field(..., description="Whether the feature toggle record is active")
    created_by: Optional[int] = Field(None, description="ID of admin who created this toggle")
    updated_by: Optional[int] = Field(None, description="ID of admin who last updated this toggle")

    class Config:
        from_attributes = True


class RuntimeConfigResponse(BaseModel):
    """Schema for runtime configuration response."""
    configurations: Dict[str, Any] = Field(..., description="Runtime configurations")
    feature_toggles: Dict[str, bool] = Field(..., description="Feature toggle states")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")
    last_updated: datetime = Field(..., description="When the configuration was last updated")


class ConfigBulkUpdate(BaseModel):
    """Schema for bulk configuration updates."""
    configurations: List[Dict[str, Any]] = Field(..., description="List of configurations to update")
    feature_toggles: List[Dict[str, Any]] = Field(default_factory=list, description="List of feature toggles to update")


class ConfigExportResponse(BaseModel):
    """Schema for configuration export."""
    configurations: List[ConfigResponse] = Field(..., description="List of configurations")
    feature_toggles: List[FeatureToggleResponse] = Field(..., description="List of feature toggles")
    exported_at: datetime = Field(..., description="When the export was generated")
    exported_by: int = Field(..., description="ID of admin who exported the configuration")


class ConfigImportRequest(BaseModel):
    """Schema for configuration import."""
    configurations: List[ConfigCreate] = Field(..., description="Configurations to import")
    feature_toggles: List[FeatureToggleCreate] = Field(default_factory=list, description="Feature toggles to import")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing configurations")
