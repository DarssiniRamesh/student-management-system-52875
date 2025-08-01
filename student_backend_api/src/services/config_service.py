"""
Configuration service for managing application settings and feature toggles.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from ..models.config import Configuration, FeatureToggle
from ..schemas.config import (
    ConfigCreate, ConfigUpdate,
    FeatureToggleCreate, FeatureToggleUpdate,
    RuntimeConfigResponse
)


class ConfigService:
    """Service class for configuration and feature toggle management."""

    def __init__(self, db: Session):
        self.db = db

    # PUBLIC_INTERFACE
    def get_configuration(self, key: str, include_sensitive: bool = False) -> Optional[Configuration]:
        """
        Get a configuration by key.
        
        Args:
            key: Configuration key
            include_sensitive: Whether to include sensitive configurations
            
        Returns:
            Configuration object or None if not found
        """
        query = self.db.query(Configuration).filter(
            Configuration.key == key,
            Configuration.is_active == True
        )
        
        if not include_sensitive:
            query = query.filter(Configuration.is_sensitive == False)
            
        return query.first()

    # PUBLIC_INTERFACE
    def get_configurations(
        self, 
        category: Optional[str] = None,
        include_sensitive: bool = False,
        include_system: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Configuration], int]:
        """
        Get configurations with filtering and pagination.
        
        Args:
            category: Filter by category
            include_sensitive: Whether to include sensitive configurations
            include_system: Whether to include system configurations
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (configurations list, total count)
        """
        query = self.db.query(Configuration).filter(Configuration.is_active == True)
        
        if category:
            query = query.filter(Configuration.category == category)
            
        if not include_sensitive:
            query = query.filter(Configuration.is_sensitive == False)
            
        if not include_system:
            query = query.filter(Configuration.is_system == False)
        
        total = query.count()
        configurations = query.offset(skip).limit(limit).all()
        
        return configurations, total

    # PUBLIC_INTERFACE
    def create_configuration(self, config_data: ConfigCreate, admin_id: int) -> Configuration:
        """
        Create a new configuration.
        
        Args:
            config_data: Configuration data
            admin_id: ID of the admin creating the configuration
            
        Returns:
            Created configuration
            
        Raises:
            HTTPException: If configuration key already exists
        """
        # Check if key already exists
        existing = self.db.query(Configuration).filter(
            Configuration.key == config_data.key,
            Configuration.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuration with key '{config_data.key}' already exists"
            )
        
        config = Configuration(
            key=config_data.key,
            value=config_data.value,
            description=config_data.description,
            category=config_data.category,
            is_sensitive=config_data.is_sensitive,
            is_system=config_data.is_system,
            created_by=admin_id,
            updated_by=admin_id
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config

    # PUBLIC_INTERFACE
    def update_configuration(
        self, 
        key: str, 
        config_data: ConfigUpdate, 
        admin_id: int,
        allow_system: bool = False
    ) -> Optional[Configuration]:
        """
        Update an existing configuration.
        
        Args:
            key: Configuration key
            config_data: Updated configuration data
            admin_id: ID of the admin updating the configuration
            allow_system: Whether to allow updating system configurations
            
        Returns:
            Updated configuration or None if not found
            
        Raises:
            HTTPException: If trying to update system configuration without permission
        """
        config = self.db.query(Configuration).filter(
            Configuration.key == key,
            Configuration.is_active == True
        ).first()
        
        if not config:
            return None
        
        if config.is_system and not allow_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update system configuration"
            )
        
        # Update fields
        update_data = config_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        config.updated_by = admin_id
        
        self.db.commit()
        self.db.refresh(config)
        
        return config

    # PUBLIC_INTERFACE
    def delete_configuration(self, key: str, allow_system: bool = False) -> bool:
        """
        Delete (soft delete) a configuration.
        
        Args:
            key: Configuration key
            allow_system: Whether to allow deleting system configurations
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            HTTPException: If trying to delete system configuration without permission
        """
        config = self.db.query(Configuration).filter(
            Configuration.key == key,
            Configuration.is_active == True
        ).first()
        
        if not config:
            return False
        
        if config.is_system and not allow_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system configuration"
            )
        
        config.is_active = False
        self.db.commit()
        
        return True

    # PUBLIC_INTERFACE
    def get_feature_toggle(self, name: str) -> Optional[FeatureToggle]:
        """
        Get a feature toggle by name.
        
        Args:
            name: Feature toggle name
            
        Returns:
            FeatureToggle object or None if not found
        """
        return self.db.query(FeatureToggle).filter(
            FeatureToggle.name == name,
            FeatureToggle.is_active == True
        ).first()

    # PUBLIC_INTERFACE
    def get_feature_toggles(
        self,
        environment: Optional[str] = None,
        enabled_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[FeatureToggle], int]:
        """
        Get feature toggles with filtering and pagination.
        
        Args:
            environment: Filter by environment
            enabled_only: Only return enabled toggles
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (feature toggles list, total count)
        """
        query = self.db.query(FeatureToggle).filter(FeatureToggle.is_active == True)
        
        if environment:
            query = query.filter(
                or_(
                    FeatureToggle.environment == environment,
                    FeatureToggle.environment == "all"
                )
            )
            
        if enabled_only:
            query = query.filter(FeatureToggle.enabled == True)
        
        total = query.count()
        toggles = query.offset(skip).limit(limit).all()
        
        return toggles, total

    # PUBLIC_INTERFACE
    def create_feature_toggle(self, toggle_data: FeatureToggleCreate, admin_id: int) -> FeatureToggle:
        """
        Create a new feature toggle.
        
        Args:
            toggle_data: Feature toggle data
            admin_id: ID of the admin creating the toggle
            
        Returns:
            Created feature toggle
            
        Raises:
            HTTPException: If feature toggle name already exists
        """
        # Check if name already exists
        existing = self.db.query(FeatureToggle).filter(
            FeatureToggle.name == toggle_data.name,
            FeatureToggle.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Feature toggle with name '{toggle_data.name}' already exists"
            )
        
        toggle = FeatureToggle(
            name=toggle_data.name,
            enabled=toggle_data.enabled,
            description=toggle_data.description,
            environment=toggle_data.environment,
            rollout_percentage=toggle_data.rollout_percentage,
            user_groups=toggle_data.user_groups,
            conditions=toggle_data.conditions,
            created_by=admin_id,
            updated_by=admin_id
        )
        
        self.db.add(toggle)
        self.db.commit()
        self.db.refresh(toggle)
        
        return toggle

    # PUBLIC_INTERFACE
    def update_feature_toggle(
        self, 
        name: str, 
        toggle_data: FeatureToggleUpdate, 
        admin_id: int
    ) -> Optional[FeatureToggle]:
        """
        Update an existing feature toggle.
        
        Args:
            name: Feature toggle name
            toggle_data: Updated toggle data
            admin_id: ID of the admin updating the toggle
            
        Returns:
            Updated feature toggle or None if not found
        """
        toggle = self.db.query(FeatureToggle).filter(
            FeatureToggle.name == name,
            FeatureToggle.is_active == True
        ).first()
        
        if not toggle:
            return None
        
        # Update fields
        update_data = toggle_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(toggle, field, value)
        
        toggle.updated_by = admin_id
        
        self.db.commit()
        self.db.refresh(toggle)
        
        return toggle

    # PUBLIC_INTERFACE
    def delete_feature_toggle(self, name: str) -> bool:
        """
        Delete (soft delete) a feature toggle.
        
        Args:
            name: Feature toggle name
            
        Returns:
            True if deleted, False if not found
        """
        toggle = self.db.query(FeatureToggle).filter(
            FeatureToggle.name == name,
            FeatureToggle.is_active == True
        ).first()
        
        if not toggle:
            return False
        
        toggle.is_active = False
        self.db.commit()
        
        return True

    # PUBLIC_INTERFACE
    def get_runtime_config(
        self, 
        environment: str = "all",
        include_sensitive: bool = False
    ) -> RuntimeConfigResponse:
        """
        Get runtime configuration for the application.
        
        Args:
            environment: Environment to get config for
            include_sensitive: Whether to include sensitive configurations
            
        Returns:
            Runtime configuration response
        """
        # Get all active configurations
        configs, _ = self.get_configurations(
            include_sensitive=include_sensitive,
            include_system=True,
            limit=1000
        )
        
        # Get all active feature toggles for environment
        toggles, _ = self.get_feature_toggles(
            environment=environment,
            limit=1000
        )
        
        # Build response
        configurations = {}
        for config in configs:
            if include_sensitive or not config.is_sensitive:
                configurations[config.key] = config.value
            else:
                configurations[config.key] = None
        
        feature_toggles = {}
        for toggle in toggles:
            feature_toggles[toggle.name] = toggle.enabled
        
        return RuntimeConfigResponse(
            configurations=configurations,
            feature_toggles=feature_toggles,
            metadata={
                "environment": environment,
                "total_configs": len(configurations),
                "total_toggles": len(feature_toggles),
                "sensitive_hidden": not include_sensitive
            },
            last_updated=datetime.utcnow()
        )

    # PUBLIC_INTERFACE
    def is_feature_enabled(
        self, 
        feature_name: str, 
        user_id: Optional[str] = None,
        user_groups: Optional[List[str]] = None,
        environment: str = "all"
    ) -> bool:
        """
        Check if a feature is enabled for a specific user/context.
        
        Args:
            feature_name: Name of the feature to check
            user_id: User ID to check
            user_groups: User's groups
            environment: Environment context
            
        Returns:
            True if feature is enabled, False otherwise
        """
        toggle = self.db.query(FeatureToggle).filter(
            FeatureToggle.name == feature_name,
            FeatureToggle.is_active == True,
            or_(
                FeatureToggle.environment == environment,
                FeatureToggle.environment == "all"
            )
        ).first()
        
        if not toggle:
            return False
        
        return toggle.is_enabled_for_user(user_id, user_groups)

    # PUBLIC_INTERFACE
    def get_categories(self) -> List[str]:
        """
        Get all unique configuration categories.
        
        Returns:
            List of unique categories
        """
        categories = self.db.query(Configuration.category).filter(
            Configuration.is_active == True
        ).distinct().all()
        
        return [cat[0] for cat in categories if cat[0]]

    # PUBLIC_INTERFACE
    def bulk_update_configs(
        self, 
        updates: List[Dict[str, Any]], 
        admin_id: int
    ) -> Dict[str, Any]:
        """
        Bulk update multiple configurations.
        
        Args:
            updates: List of configuration updates
            admin_id: ID of the admin performing updates
            
        Returns:
            Results summary
        """
        results = {
            "updated": 0,
            "created": 0,
            "errors": []
        }
        
        for update in updates:
            try:
                key = update.get("key")
                if not key:
                    results["errors"].append("Missing key in update")
                    continue
                
                existing = self.get_configuration(key, include_sensitive=True)
                
                if existing:
                    # Update existing
                    config_update = ConfigUpdate(**{k: v for k, v in update.items() if k != "key"})
                    self.update_configuration(key, config_update, admin_id, allow_system=True)
                    results["updated"] += 1
                else:
                    # Create new
                    config_create = ConfigCreate(**update)
                    self.create_configuration(config_create, admin_id)
                    results["created"] += 1
                    
            except Exception as e:
                results["errors"].append(f"Error updating {update.get('key', 'unknown')}: {str(e)}")
        
        return results
