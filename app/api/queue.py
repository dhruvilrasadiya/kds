"""
Queue API endpoints for the Smart Kitchen Queue Management System.
All operations use MongoDB exclusively.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from datetime import datetime

from app.models import BaseResponse
from app.services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)

router = APIRouter()


def get_services(request: Request):
    """Dependency to get services from app state."""
    return {
        'mongodb_service': request.app.state.mongodb_service,
        'queue_manager': request.app.state.queue_manager,
    }


@router.get("/items")
async def get_queue_items(
    kitchen_id: Optional[str] = Query(None, description="Filter by kitchen ID"),
    order_id: Optional[str] = Query(None, description="Filter by order ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Maximum number of items to return"),
    services=Depends(get_services)
):
    """Get queue items from MongoDB with optional filtering."""
    try:
        # Get queue items from MongoDB
        queue_items = await services['mongodb_service'].get_queue_items(
            kitchen_id=kitchen_id,
            status=status,
            order_id=order_id
        )
        
        # Apply limit
        if limit and len(queue_items) > limit:
            queue_items = queue_items[:limit]
        
        # Add kitchen and item details
        for item in queue_items:
            # Get menu item details
            menu_item = await services['mongodb_service'].get_menu_item(item.get('item_id'))
            if menu_item:
                item['item_name'] = menu_item.get('item_name', menu_item.get('name', 'Unknown'))
                item['category'] = menu_item.get('category', 'general')
            
            # Get kitchen details
            kitchens = await services['mongodb_service'].get_kitchens()
            kitchen_info = next((k for k in kitchens if k['kitchen_id'] == item.get('kitchen_id')), None)
            if kitchen_info:
                item['kitchen_name'] = kitchen_info.get('kitchen_name', kitchen_info.get('name', 'Unknown'))
        
        return {
            "success": True,
            "message": f"Retrieved {len(queue_items)} queue items",
            "queue_items": queue_items,
            "total_count": len(queue_items),
            "filters": {
                "kitchen_id": kitchen_id,
                "order_id": order_id,
                "status": status,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting queue items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/items/{queue_id}/status")
async def update_queue_item_status(
    queue_id: str,
    status: str,
    services=Depends(get_services)
):
    """Update queue item status in MongoDB."""
    try:
        # Validate status
        valid_statuses = ['queued', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        # Update status in MongoDB
        additional_data = {}
        if status == "in_progress":
            additional_data["actual_start"] = datetime.now()
        elif status == "completed":
            additional_data["actual_completion"] = datetime.now()
        
        success = await services['mongodb_service'].update_queue_item_status(
            queue_id, 
            status,
            **additional_data
        )
        
        if success:
            return {
                "success": True,
                "message": f"Queue item {queue_id} status updated to {status}",
                "queue_id": queue_id,
                "new_status": status,
                "updated_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Queue item {queue_id} not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating queue item status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/{queue_id}")
async def get_queue_item(
    queue_id: str,
    services=Depends(get_services)
):
    """Get a specific queue item by ID from MongoDB."""
    try:
        # Get all queue items and find the specific one
        all_items = await services['mongodb_service'].get_queue_items()
        queue_item = next((item for item in all_items if item.get('queue_id') == queue_id), None)
        
        if not queue_item:
            raise HTTPException(
                status_code=404,
                detail=f"Queue item {queue_id} not found"
            )
        
        # Add additional details
        menu_item = await services['mongodb_service'].get_menu_item(queue_item.get('item_id'))
        if menu_item:
            queue_item['item_name'] = menu_item.get('item_name', menu_item.get('name', 'Unknown'))
            queue_item['category'] = menu_item.get('category', 'general')
        
        kitchens = await services['mongodb_service'].get_kitchens()
        kitchen_info = next((k for k in kitchens if k['kitchen_id'] == queue_item.get('kitchen_id')), None)
        if kitchen_info:
            queue_item['kitchen_name'] = kitchen_info.get('kitchen_name', kitchen_info.get('name', 'Unknown'))
        
        return {
            "success": True,
            "message": f"Queue item {queue_id} retrieved successfully",
            "queue_item": queue_item
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting queue item {queue_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/items/{queue_id}")
async def delete_queue_item(
    queue_id: str,
    services=Depends(get_services)
):
    """Delete a queue item from MongoDB."""
    try:
        # For now, we'll mark as cancelled instead of deleting
        success = await services['mongodb_service'].update_queue_item_status(
            queue_id, 
            "cancelled"
        )
        
        if success:
            return {
                "success": True,
                "message": f"Queue item {queue_id} cancelled successfully",
                "queue_id": queue_id,
                "action": "cancelled"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Queue item {queue_id} not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting queue item {queue_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_queue_stats(services=Depends(get_services)):
    """Get queue statistics from MongoDB."""
    try:
        # Get all queue items
        all_items = await services['mongodb_service'].get_queue_items()
        
        # Calculate statistics
        stats = {
            "total_items": len(all_items),
            "by_status": {},
            "by_kitchen": {},
            "average_prep_time": 0,
            "oldest_item": None,
            "newest_item": None
        }
        
        if all_items:
            # Count by status
            for item in all_items:
                status = item.get('status', 'unknown')
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                kitchen_id = item.get('kitchen_id', 'unknown')
                stats["by_kitchen"][kitchen_id] = stats["by_kitchen"].get(kitchen_id, 0) + 1
            
            # Calculate average prep time
            prep_times = [item.get('prep_time_minutes', 0) for item in all_items]
            stats["average_prep_time"] = sum(prep_times) / len(prep_times) if prep_times else 0
            
            # Find oldest and newest items
            items_with_dates = [item for item in all_items if item.get('created_at')]
            if items_with_dates:
                oldest = min(items_with_dates, key=lambda x: x['created_at'])
                newest = max(items_with_dates, key=lambda x: x['created_at'])
                stats["oldest_item"] = {
                    "queue_id": oldest.get('queue_id'),
                    "created_at": oldest.get('created_at'),
                    "item_id": oldest.get('item_id')
                }
                stats["newest_item"] = {
                    "queue_id": newest.get('queue_id'),
                    "created_at": newest.get('created_at'),
                    "item_id": newest.get('item_id')
                }
        
        return {
            "success": True,
            "message": "Queue statistics retrieved successfully",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
