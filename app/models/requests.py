"""
Request models for the Smart Kitchen Queue Management System API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CreateOrderRequest(BaseModel):
    """Request model for creating a new order."""
    items: List[str] = Field(..., min_items=1, description="List of item IDs to order")
    customer_id: Optional[str] = Field(None, description="Optional customer identifier")
    notes: Optional[str] = Field(None, description="Optional order notes")


class UpdateOrderRequest(BaseModel):
    """Request model for updating an order."""
    status: Optional[str] = Field(None, description="New order status")
    notes: Optional[str] = Field(None, description="Updated order notes")


class CompleteItemRequest(BaseModel):
    """Request model for marking an item as completed."""
    actual_completion_time: Optional[datetime] = Field(None, description="Actual completion time")
    notes: Optional[str] = Field(None, description="Completion notes")


class KitchenStatusUpdateRequest(BaseModel):
    """Request model for updating kitchen status."""
    status: str = Field(..., description="New kitchen status")
    notes: Optional[str] = Field(None, description="Status update notes")


class ReloadConfigRequest(BaseModel):
    """Request model for reloading system configuration."""
    force_reload: bool = Field(False, description="Force reload even if no changes detected")
    clear_cache: bool = Field(True, description="Clear all cached data")


class PerformanceQueryRequest(BaseModel):
    """Request model for querying performance data."""
    start_date: Optional[datetime] = Field(None, description="Start date for query")
    end_date: Optional[datetime] = Field(None, description="End date for query")
    kitchen_id: Optional[str] = Field(None, description="Filter by kitchen ID")
    item_id: Optional[str] = Field(None, description="Filter by item ID")
    limit: int = Field(100, gt=0, le=1000, description="Maximum number of records to return")
