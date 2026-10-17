"""
Kitchens API endpoints for the Smart Kitchen Queue Management System.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request

from app.models import (
    CompleteItemRequest, KitchenStatusUpdateRequest,
    KitchenStatusResponse, KitchenStatusListResponse,
    ItemStatus, BaseResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_services(request: Request):
    """Dependency to get services from app state."""
    return {
        'excel_service': request.app.state.excel_service,
        'mongodb_service': request.app.state.mongodb_service,
        'data_sync_service': request.app.state.data_sync_service,
        'queue_manager': request.app.state.queue_manager,
        'starvation_prevention': request.app.state.starvation_prevention,
        'ai_agent': request.app.state.ai_agent,
        'performance_learning': request.app.state.performance_learning
    }


@router.get("/")
async def get_all_kitchens(services=Depends(get_services)):
    """Get all kitchens with their current status."""
    try:
        # Get kitchen configurations from MongoDB
        kitchens_list = await services['mongodb_service'].get_kitchens()

        # Get current queue status for each kitchen using MongoDB-based queue manager
        for kitchen in kitchens_list:
            try:
                current_load = await services['queue_manager'].get_kitchen_current_load(kitchen['kitchen_id'])
                kitchen['current_load'] = current_load
            except Exception as e:
                logger.warning(f"Error getting load for kitchen {kitchen['kitchen_id']}: {e}")
                kitchen['current_load'] = 0

        return {
            "success": True,
            "message": f"Retrieved {len(kitchens_list)} kitchens",
            "kitchens": kitchens_list,
            "total_active_orders": sum(k.get('current_load', 0) for k in kitchens_list)
        }

    except Exception as e:
        logger.error(f"Error getting kitchens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=KitchenStatusListResponse)
async def get_all_kitchen_statuses(services=Depends(get_services)):
    """Get status for all kitchens using MongoDB-based queue manager."""
    try:
        kitchen_statuses = await services['queue_manager'].get_all_kitchen_statuses()

        return KitchenStatusListResponse(
            success=True,
            message=f"Retrieved status for {len(kitchen_statuses)} kitchens",
            kitchen_statuses=kitchen_statuses
        )

    except Exception as e:
        logger.error(f"Error getting kitchen statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kitchen_id}", response_model=KitchenStatusResponse)
async def get_kitchen_status(kitchen_id: str, services=Depends(get_services)):
    """Get status for a specific kitchen using MongoDB-based queue manager."""
    try:
        kitchen_status = await services['queue_manager'].get_kitchen_status(kitchen_id)

        if not kitchen_status:
            raise HTTPException(
                status_code=404,
                detail=f"Kitchen {kitchen_id} not found"
            )

        return KitchenStatusResponse(
            success=True,
            message=f"Kitchen {kitchen_id} status retrieved successfully",
            kitchen_status=kitchen_status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting kitchen {kitchen_id} status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{kitchen_id}/complete/{item_id}", response_model=BaseResponse)
async def complete_item(
    kitchen_id: str,
    item_id: str,
    completion_request: CompleteItemRequest,
    services=Depends(get_services)
):
    """Mark an item as completed in a kitchen."""
    try:
        # Get the item from the queue to record performance using MongoDB-based queue manager
        kitchen_status = await services['queue_manager'].get_kitchen_status(kitchen_id)
        if not kitchen_status:
            raise HTTPException(
                status_code=404,
                detail=f"Kitchen {kitchen_id} not found"
            )

        # Find the item in the queue
        queue_item = None
        for item in kitchen_status.current_queue:
            if item.item_id == item_id:
                queue_item = item
                break

        if not queue_item:
            raise HTTPException(
                status_code=404,
                detail=f"Item {item_id} not found in kitchen {kitchen_id} queue"
            )

        # Calculate actual completion time
        actual_completion = completion_request.actual_completion_time or datetime.now()

        # Calculate actual prep time
        if queue_item.actual_start:
            actual_prep_time = int((actual_completion - queue_item.actual_start).total_seconds() / 60)
        else:
            # If no actual start time, use scheduled prep time
            actual_prep_time = queue_item.prep_time

        # Mark item as completed using MongoDB-based queue manager
        success = await services['queue_manager'].remove_completed_item(kitchen_id, item_id)
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to complete item {item_id}"
            )
        
        # Record performance data
        services['performance_learning'].record_completion(
            item_id=item_id,
            kitchen_id=kitchen_id,
            order_id=queue_item.order_id,
            actual_time=actual_prep_time,
            scheduled_time=queue_item.prep_time,
            priority_level=queue_item.priority_level,
            kitchen_load=kitchen_status.current_load,
            starvation_count=queue_item.starvation_count
        )
        
        # Reset starvation counters for this item
        services['starvation_prevention'].reset_item_counters(item_id)
        
        # Check if all items in the order are completed and update order status if needed
        if queue_item.order_id:
            # Get all queue items for this order
            order_items = await services['mongodb_service'].get_queue_items(order_id=queue_item.order_id)
            
            # Check if all items are completed
            all_completed = all(item.get('status') == 'completed' for item in order_items)
            
            if all_completed:
                # Update order status to completed in MongoDB
                await services['mongodb_service'].update_order_status(queue_item.order_id, "completed")
                logger.info(f"All items completed for order {queue_item.order_id}, marked as completed")
        
        logger.info(f"Completed item {item_id} in kitchen {kitchen_id}")
        
        return BaseResponse(
            success=True,
            message=f"Item {item_id} completed successfully in kitchen {kitchen_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing item {item_id} in kitchen {kitchen_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{kitchen_id}/start/{item_id}", response_model=BaseResponse)
async def start_item(kitchen_id: str, item_id: str, services=Depends(get_services)):
    """Mark an item as started in a kitchen."""
    try:
        # Update item status to in progress
        success = services['queue_manager'].update_item_status(
            kitchen_id, item_id, ItemStatus.IN_PROGRESS, datetime.now()
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Item {item_id} not found in kitchen {kitchen_id} queue"
            )
        
        logger.info(f"Started item {item_id} in kitchen {kitchen_id}")
        
        return BaseResponse(
            success=True,
            message=f"Item {item_id} started successfully in kitchen {kitchen_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting item {item_id} in kitchen {kitchen_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{kitchen_id}/status", response_model=KitchenStatusResponse)
async def update_kitchen_status(
    kitchen_id: str,
    status_request: KitchenStatusUpdateRequest,
    services=Depends(get_services)
):
    """Update kitchen status."""
    try:
        # This would typically update the kitchen status in the database
        # For now, we'll just return the current status
        kitchen_status = services['queue_manager'].get_kitchen_status(kitchen_id)
        
        if not kitchen_status:
            raise HTTPException(
                status_code=404,
                detail=f"Kitchen {kitchen_id} not found"
            )
        
        logger.info(f"Kitchen {kitchen_id} status update requested: {status_request.status}")
        
        return KitchenStatusResponse(
            success=True,
            message=f"Kitchen {kitchen_id} status updated to {status_request.status}",
            kitchen_status=kitchen_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating kitchen {kitchen_id} status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kitchen_id}/efficiency", response_model=dict)
async def get_kitchen_efficiency(kitchen_id: str, days: int = 7, services=Depends(get_services)):
    """Get efficiency metrics for a kitchen."""
    try:
        efficiency_data = services['performance_learning'].analyze_kitchen_efficiency(
            kitchen_id, days
        )
        
        return {
            "success": True,
            "message": f"Kitchen {kitchen_id} efficiency data retrieved",
            "data": efficiency_data
        }
        
    except Exception as e:
        logger.error(f"Error getting kitchen {kitchen_id} efficiency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kitchen_id}/reorder-queue", response_model=BaseResponse)
async def reorder_kitchen_queue(kitchen_id: str, services=Depends(get_services)):
    """Reorder kitchen queue based on current priorities."""
    try:
        await services['queue_manager'].reorder_queue_by_priority(kitchen_id)
        
        return BaseResponse(
            success=True,
            message=f"Kitchen {kitchen_id} queue reordered successfully"
        )
        
    except Exception as e:
        logger.error(f"Error reordering kitchen {kitchen_id} queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kitchen_id}/completed", response_model=BaseResponse)
async def clear_completed_items(
    kitchen_id: str,
    hours: int = 24,
    services=Depends(get_services)
):
    """Clear completed items from kitchen queue."""
    try:
        services['queue_manager'].clear_completed_items(kitchen_id, hours)
        
        return BaseResponse(
            success=True,
            message=f"Cleared completed items older than {hours} hours from kitchen {kitchen_id}"
        )
        
    except Exception as e:
        logger.error(f"Error clearing completed items from kitchen {kitchen_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
