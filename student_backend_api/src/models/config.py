"""
Configuration and feature toggle model definitions.
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class Configuration(BaseModel):
    """
    Configuration model for storing application settings and runtime configurations.
    
    Attributes:
        key: Unique configuration key
        value: Configuration value (JSON field supporting multiple data types)
        description: Optional description of the configuration
        category: Configuration category for grouping
        is_sensitive: Whether the configuration contains sensitive data
        is_system: Whether this is a system-level configuration
        created_by: ID of admin who created this configuration
        updated_by: ID of admin who last updated this configuration
    """
    __tablename__ = "configurations"

    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    is_sensitive = Column(Boolean, default=False, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey("admins.id"))
    updated_by = Column(Integer, ForeignKey("admins.id"))

    # Relationships
    creator = relationship("Admin", foreign_keys=[created_by], backref="created_configs")
    updater = relationship("Admin", foreign_keys=[updated_by], backref="updated_configs")

    def __repr__(self) -> str:
        return f"<Configuration(id={self.id}, key={self.key}, category={self.category})>"

    def to_dict_safe(self) -> dict:
        """Convert to dictionary, hiding sensitive values."""
        data = self.to_dict()
        if self.is_sensitive:
            data['value'] = '***HIDDEN***'
        return data


class FeatureToggle(BaseModel):
    """
    Feature toggle model for managing feature flags and A/B testing.
    
    Attributes:
        name: Unique feature name
        enabled: Whether the feature is enabled
        description: Optional description of the feature
        environment: Environment where this toggle applies
        rollout_percentage: Percentage of users who should see this feature (0-100)
        user_groups: List of user groups that have access to this feature
        conditions: Additional conditions for feature activation
        created_by: ID of admin who created this feature toggle
        updated_by: ID of admin who last updated this feature toggle
    """
    __tablename__ = "feature_toggles"

    name = Column(String(255), unique=True, index=True, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    description = Column(Text)
    environment = Column(String(50), default="all", nullable=False, index=True)
    rollout_percentage = Column(Float, default=0.0, nullable=False)
    user_groups = Column(JSON, default=list)
    conditions = Column(JSON, default=dict)
    created_by = Column(Integer, ForeignKey("admins.id"))
    updated_by = Column(Integer, ForeignKey("admins.id"))

    # Relationships
    creator = relationship("Admin", foreign_keys=[created_by], backref="created_toggles")
    updater = relationship("Admin", foreign_keys=[updated_by], backref="updated_toggles")

    def __repr__(self) -> str:
        return f"<FeatureToggle(id={self.id}, name={self.name}, enabled={self.enabled})>"

    def is_enabled_for_user(self, user_id: str = None, user_groups: list = None) -> bool:
        """
        Check if feature is enabled for a specific user.
        
        Args:
            user_id: User ID to check
            user_groups: User's groups
            
        Returns:
            bool: True if feature is enabled for the user
        """
        if not self.enabled:
            return False
        
        # Check rollout percentage
        if self.rollout_percentage < 100.0:
            import hashlib
            if user_id:
                # Use user ID to determine if they're in the rollout
                hash_value = int(hashlib.md5(f"{self.name}:{user_id}".encode()).hexdigest(), 16)
                percentage = (hash_value % 100) + 1
                if percentage > self.rollout_percentage:
                    return False
        
        # Check user groups
        if self.user_groups and user_groups:
            if not any(group in self.user_groups for group in user_groups):
                return False
        
        # Check additional conditions (can be extended)
        if self.conditions:
            # Add custom condition logic here as needed
            pass
        
        return True
