"""
Orders API endpoints for the Smart Kitchen Queue Management System.
"""

import logging
import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from app.models import (
    CreateOrderRequest, UpdateOrderRequest, OrderResponse, OrderListResponse,
    Order, OrderStatus, ErrorResponse, QueueItem, ItemStatus, PriorityLevel
)
from app.services.mongodb_service import mongodb_service

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


# In-memory order storage (in production, use a proper database)
orders_storage = {}


@router.post("/", response_model=OrderResponse)
async def create_order(order_request: CreateOrderRequest, services=Depends(get_services)):
    """Create a new order and optimize its schedule."""
    try:
        # Generate unique order ID
        order_id = f"ORD_{uuid.uuid4().hex[:8].upper()}"
        
        # Validate items using MongoDB service
        validation_results = await services['mongodb_service'].validate_order_items(order_request.items)
        logger.info(f"Validation results: {validation_results}")
        invalid_items = [item_id for item_id, valid in validation_results.items() if not valid]

        if invalid_items:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": "One or more items are invalid or unavailable",
                    "invalid_items": invalid_items,
                    "error_code": 400
                }
            )
        
        # Create order
        order = Order(
            order_id=order_id,
            items=order_request.items,
            timestamp=datetime.now(),
            status=OrderStatus.PENDING
        )
        
        # Use AI agent to optimize schedule
        optimization_result = await services['ai_agent'].optimize_order_schedule(
            order_request.items, order_id
        )
        
        # Update order with optimization results
        order.queue_items = optimization_result.optimized_items
        order.total_prep_time = optimization_result.total_estimated_time
        order.status = OrderStatus.PROCESSING
        
        # Calculate estimated completion time
        if optimization_result.optimized_items:
            order.estimated_completion = max(
                item.estimated_completion for item in optimization_result.optimized_items
            )
        
        # Add items to kitchen queues (MongoDB-based queue manager)
        for queue_item in optimization_result.optimized_items:
            # Set order_id for the queue item
            queue_item.order_id = order_id


            # Add to MongoDB-based queue manager (this handles MongoDB storage)
            success = await services['queue_manager'].add_item_to_queue(
                queue_item.kitchen_id, queue_item
            )
            if not success:
                logger.warning(f"Failed to add item {queue_item.item_id} to queue")

        # Store order in MongoDB
        order_data = {
            "order_id": order_id,
            "items": order_request.items,
            "customer_id": getattr(order_request, 'customer_id', None),
            "notes": getattr(order_request, 'notes', None),
            "status": order.status.value,
            "timestamp": order.timestamp,
            "total_prep_time": order.total_prep_time,
            "estimated_completion": order.estimated_completion,
            "queue_items_count": len(optimization_result.optimized_items),
            "queue_items" : optimization_result.optimized_items
        }

        stored_order_id = await services['mongodb_service'].create_order(order_data)
        if not stored_order_id:
            logger.error(f"Failed to store order {order_id} in MongoDB")
            # Continue anyway as the order processing succeeded
        
        logger.info(f"Created order {order_id} with {len(order_request.items)} items")
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} created successfully",
            order=order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, services=Depends(get_services)):
    """Get order details by ID."""
    try:
        # Get order from MongoDB
        order_data = await services['mongodb_service'].get_order_by_id(order_id)
        if not order_data:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        
        # Get queue items for this order
        queue_items = await services['mongodb_service'].get_queue_items(order_id=order_id)

        # Convert to Order model
        order = Order(
            order_id=order_data["order_id"],
            items=order_data["items"],
            timestamp=order_data["timestamp"],
            status=OrderStatus(order_data["status"]),
            total_prep_time=order_data.get("total_prep_time"),
            estimated_completion=order_data.get("estimated_completion")
        )
        
        # Update order status based on queue items
        if queue_items:
            completed_items = sum(1 for item in queue_items if item.get("status") == "completed")
            total_items = len(queue_items)

            if completed_items == total_items:
                order.status = OrderStatus.COMPLETED
                # Update in MongoDB if status changed
                if order_data["status"] != "completed":
                    await services['mongodb_service'].update_order_status(order_id, "completed")
            elif completed_items > 0:
                order.status = OrderStatus.PROCESSING
                # Update in MongoDB if status changed
                if order_data["status"] == "pending":
                    await services['mongodb_service'].update_order_status(order_id, "preparing")
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} retrieved successfully",
            order=order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    services=Depends(get_services)
):
    """List orders with optional filtering."""
    try:
        # Get orders from MongoDB
        orders_data = await services['mongodb_service'].get_orders(status=status, limit=limit + offset)
        print(f"Retrieved ++++++++++  {orders_data} ++++++++++ orders from MongoDB")

        # Convert to Order models
        orders_list = []
        for order_data in orders_data[offset:]:
            # Get queue items for this order
            queue_items_data = await services['mongodb_service'].get_queue_items(order_id=order_data["order_id"])
            
            # Convert queue items to QueueItem models
            queue_items = []
            for item_data in queue_items_data:
                try:
                    queue_item = QueueItem(
                        item_id=item_data.get('item_id', ''),
                        item_name=item_data.get('item_name', ''),
                        order_id=item_data.get('order_id', ''),
                        prep_time=item_data.get('prep_time_minutes', 10),
                        scheduled_start=item_data.get('scheduled_start', datetime.now()),
                        estimated_completion=item_data.get('estimated_completion', datetime.now()),
                        status=ItemStatus(item_data.get('status', 'queued')),
                        priority_level=PriorityLevel(item_data.get('priority_level', 'normal')),
                        kitchen_id=item_data.get('kitchen_id', ''),
                        starvation_count=item_data.get('starvation_count', 0)
                    )
                    queue_items.append(queue_item)
                except Exception as e:
                    logger.warning(f"Error converting queue item: {e}")
                    continue
            
            order = Order(
                order_id=order_data["order_id"],
                items=order_data["items"],
                timestamp=order_data["timestamp"],
                status=OrderStatus(order_data["status"]),
                total_prep_time=order_data.get("total_prep_time"),
                estimated_completion=order_data.get("estimated_completion"),
                queue_items=queue_items
            )
            orders_list.append(order)

        total_count = len(orders_data)
        
        return OrderListResponse(
            success=True,
            message=f"Retrieved {len(orders_list)} orders",
            orders=orders_list,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    update_request: UpdateOrderRequest,
    services=Depends(get_services)
):
    """Update an existing order."""
    try:
        # Get order from MongoDB
        order_data = await services['mongodb_service'].get_order_by_id(order_id)
        if not order_data:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        # Update status if provided
        if update_request.status:
            try:
                new_status = OrderStatus(update_request.status)

                # Update in MongoDB
                success = await services['mongodb_service'].update_order_status(order_id, update_request.status)
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to update order in database")

            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {update_request.status}"
                )

        # Get updated order
        updated_order_data = await services['mongodb_service'].get_order_by_id(order_id)
        order = Order(
            order_id=updated_order_data["order_id"],
            items=updated_order_data["items"],
            timestamp=updated_order_data["timestamp"],
            status=OrderStatus(updated_order_data["status"]),
            total_prep_time=updated_order_data.get("total_prep_time"),
            estimated_completion=updated_order_data.get("estimated_completion")
        )
        
        logger.info(f"Updated order {order_id}")
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} updated successfully",
            order=order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str, services=Depends(get_services)):
    """Cancel an existing order."""
    try:
        # Get order from MongoDB
        order_data = await services['mongodb_service'].get_order_by_id(order_id)
        if not order_data:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        if order_data["status"] == "completed":
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel a completed order"
            )

        # Get and cancel all queue items using MongoDB-based queue manager
        queue_items = await services['mongodb_service'].get_queue_items(order_id=order_id)
        for queue_item in queue_items:
            if queue_item.get("status") != "completed":
                # Update using MongoDB-based queue manager (handles MongoDB updates)
                await services['queue_manager'].update_item_status(
                    queue_item["kitchen_id"],
                    queue_item["item_id"],
                    "cancelled"
                )

        # Update order status in MongoDB
        await services['mongodb_service'].update_order_status(order_id, "cancelled")

        # Get updated order
        updated_order_data = await services['mongodb_service'].get_order_by_id(order_id)
        order = Order(
            order_id=updated_order_data["order_id"],
            items=updated_order_data["items"],
            timestamp=updated_order_data["timestamp"],
            status=OrderStatus(updated_order_data["status"]),
            total_prep_time=updated_order_data.get("total_prep_time"),
            estimated_completion=updated_order_data.get("estimated_completion")
        )
        
        logger.info(f"Cancelled order {order_id}")
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} cancelled successfully",
            order=order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status: str,
    services=Depends(get_services)
):
    """Update order status directly."""
    try:
        # Validate status
        try:
            new_status = OrderStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {status}. Valid statuses: {[s.value for s in OrderStatus]}"
            )

        # Get order from MongoDB
        order_data = await services['mongodb_service'].get_order_by_id(order_id)
        if not order_data:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        # Update status in MongoDB
        success = await services['mongodb_service'].update_order_status(order_id, status)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update order status")

        # Get updated order
        updated_order_data = await services['mongodb_service'].get_order_by_id(order_id)
        order = Order(
            order_id=updated_order_data["order_id"],
            items=updated_order_data["items"],
            timestamp=updated_order_data["timestamp"],
            status=OrderStatus(updated_order_data["status"]),
            total_prep_time=updated_order_data.get("total_prep_time"),
            estimated_completion=updated_order_data.get("estimated_completion")
        )
        
        logger.info(f"Updated order {order_id} status to {status}")
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} status updated to {status}",
            order=order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

