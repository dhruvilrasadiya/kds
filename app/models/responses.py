"""
Response models for the Smart Kitchen Queue Management System API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.base import Order, KitchenStatus, QueueItem, PerformanceRecord


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class OrderResponse(BaseResponse):
    """Response model for order operations."""
    order: Optional[Order] = Field(None, description="Order data")


class OrderListResponse(BaseResponse):
    """Response model for listing orders."""
    orders: List[Order] = Field(default_factory=list, description="List of orders")
    total_count: int = Field(0, description="Total number of orders")


class KitchenStatusResponse(BaseResponse):
    """Response model for kitchen status operations."""
    kitchen_status: Optional[KitchenStatus] = Field(None, description="Kitchen status data")


class KitchenStatusListResponse(BaseResponse):
    """Response model for listing kitchen statuses."""
    kitchen_statuses: List[KitchenStatus] = Field(default_factory=list, description="List of kitchen statuses")


class QueueStatusResponse(BaseResponse):
    """Response model for queue status."""
    queue_items: List[QueueItem] = Field(default_factory=list, description="Current queue items")
    total_items: int = Field(0, description="Total number of items in queue")
    kitchen_loads: Dict[str, int] = Field(default_factory=dict, description="Current load per kitchen")


class PerformanceMetricsResponse(BaseResponse):
    """Response model for performance metrics."""
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    period_start: Optional[datetime] = Field(None, description="Metrics period start")
    period_end: Optional[datetime] = Field(None, description="Metrics period end")


class PerformanceHistoryResponse(BaseResponse):
    """Response model for performance history."""
    records: List[PerformanceRecord] = Field(default_factory=list, description="Performance records")
    total_count: int = Field(0, description="Total number of records")


class SystemHealthResponse(BaseResponse):
    """Response model for system health check."""
    status: str = Field(..., description="System status")
    components: Dict[str, str] = Field(default_factory=dict, description="Component statuses")
    uptime: Optional[str] = Field(None, description="System uptime")
    version: Optional[str] = Field(None, description="System version")


class ConfigReloadResponse(BaseResponse):
    """Response model for configuration reload."""
    reloaded_components: List[str] = Field(default_factory=list, description="Components that were reloaded")
    cache_cleared: bool = Field(False, description="Whether cache was cleared")


class ErrorResponse(BaseResponse):
    """Response model for errors."""
    error_code: Optional[str] = Field(None, description="Error code")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    
    def __init__(self, message: str, error_code: Optional[str] = None, **kwargs):
        super().__init__(success=False, message=message, **kwargs)
        self.error_code = error_code
