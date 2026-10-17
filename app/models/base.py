"""
Base models for the Smart Kitchen Queue Management System.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.enums import (
    OrderStatus, ItemStatus, KitchenStatus as KitchenStatusEnum, 
    PriorityLevel, DifficultyLevel
)


class MenuItem(BaseModel):
    """Menu item model."""
    item_id: str = Field(..., description="Unique item identifier")
    item_name: str = Field(..., description="Display name of the item")
    kitchen_id: str = Field(..., description="Kitchen responsible for this item")
    prep_time_minutes: int = Field(..., gt=0, description="Estimated preparation time in minutes")
    difficulty_level: DifficultyLevel = Field(..., description="Difficulty level of preparation")
    available: bool = Field(True, description="Whether the item is currently available")


class Kitchen(BaseModel):
    """Kitchen model."""
    kitchen_id: str = Field(..., description="Unique kitchen identifier")
    kitchen_name: str = Field(..., description="Display name of the kitchen")
    capacity: int = Field(..., gt=0, description="Maximum concurrent items the kitchen can handle")
    specialization: str = Field(..., description="Kitchen specialization description")
    status: KitchenStatusEnum = Field(KitchenStatusEnum.ACTIVE, description="Current kitchen status")


class QueueItem(BaseModel):
    """Queue item model representing an item in a kitchen queue."""
    item_id: str = Field(..., description="Menu item identifier")
    item_name: str = Field(..., description="Display name of the item")
    order_id: str = Field(..., description="Order this item belongs to")
    prep_time: int = Field(..., gt=0, description="Estimated preparation time in minutes")
    scheduled_start: datetime = Field(..., description="Scheduled start time")
    estimated_completion: datetime = Field(..., description="Estimated completion time")
    actual_start: Optional[datetime] = Field(None, description="Actual start time")
    actual_completion: Optional[datetime] = Field(None, description="Actual completion time")
    priority_level: PriorityLevel = Field(PriorityLevel.NORMAL, description="Priority level")
    starvation_count: int = Field(0, ge=0, description="Number of times this item was delayed")
    status: ItemStatus = Field(ItemStatus.QUEUED, description="Current item status")
    kitchen_id: str = Field(..., description="Kitchen assigned to prepare this item")


class Order(BaseModel):
    """Order model."""
    order_id: str = Field(..., description="Unique order identifier")
    items: List[str] = Field(..., min_items=1, description="List of item IDs in this order")
    timestamp: datetime = Field(default_factory=datetime.now, description="Order creation timestamp")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current order status")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    actual_completion: Optional[datetime] = Field(None, description="Actual completion time")
    queue_items: List[QueueItem] = Field(default_factory=list, description="Queue items for this order")
    total_prep_time: Optional[int] = Field(None, description="Total estimated preparation time")
    synchronization_window: int = Field(3, description="Minutes within which all items should complete")


class KitchenStatus(BaseModel):
    """Kitchen status model."""
    kitchen_id: str = Field(..., description="Kitchen identifier")
    kitchen_name: str = Field(..., description="Kitchen display name")
    current_queue: List[QueueItem] = Field(default_factory=list, description="Current queue items")
    capacity: int = Field(..., gt=0, description="Maximum capacity")
    current_load: int = Field(0, ge=0, description="Current number of items being processed")
    available_slots: int = Field(..., ge=0, description="Available slots for new items")
    next_available_time: datetime = Field(default_factory=datetime.now, description="Next available time slot")
    status: KitchenStatusEnum = Field(KitchenStatusEnum.ACTIVE, description="Kitchen status")
    specialization: str = Field(..., description="Kitchen specialization")


class PerformanceRecord(BaseModel):
    """Performance record model for historical tracking."""
    date: datetime = Field(..., description="Date of the performance record")
    kitchen_id: str = Field(..., description="Kitchen identifier")
    item_id: str = Field(..., description="Item identifier")
    order_id: str = Field(..., description="Order identifier")
    actual_prep_time: int = Field(..., gt=0, description="Actual preparation time in minutes")
    scheduled_prep_time: int = Field(..., gt=0, description="Scheduled preparation time in minutes")
    delay_minutes: int = Field(0, ge=0, description="Delay in minutes")
    kitchen_load: int = Field(..., ge=0, description="Kitchen load at the time")
    priority_level: PriorityLevel = Field(PriorityLevel.NORMAL, description="Priority level used")
    starvation_count: int = Field(0, ge=0, description="Starvation count at the time")


class ScheduleOptimizationResult(BaseModel):
    """Result of schedule optimization."""
    order_id: str = Field(..., description="Order identifier")
    optimized_items: List[QueueItem] = Field(..., description="Optimized queue items")
    total_estimated_time: int = Field(..., description="Total estimated completion time")
    synchronization_achieved: bool = Field(..., description="Whether synchronization was achieved")
    anti_starvation_applied: List[str] = Field(default_factory=list, description="Items with anti-starvation applied")
    optimization_notes: str = Field("", description="Notes about the optimization process")
