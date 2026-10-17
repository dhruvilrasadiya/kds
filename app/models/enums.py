"""
Enums for the Smart Kitchen Queue Management System.
"""

from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "cooking"
    PROCESSING = "preparing"
    READY = "ready"
    CANCELLED = "on-hold"
    COMPLETED = "completed"


class ItemStatus(str, Enum):
    """Item status enumeration."""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class KitchenStatus(str, Enum):
    """Kitchen status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class PriorityLevel(str, Enum):
    """Priority level enumeration."""
    NONE = "none"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
