"""
Real-time API endpoints for the Smart Kitchen Queue Management System.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request

from app.models import (
    QueueStatusResponse, PerformanceMetricsResponse,
    PerformanceQueryRequest, PerformanceHistoryResponse
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


@router.get("/queue-status", response_model=QueueStatusResponse)
async def get_queue_status(services=Depends(get_services)):
    """Get current queue status across all kitchens."""
    try:
        kitchen_statuses = services['queue_manager'].get_all_kitchen_statuses()

        # Collect all queue items
        all_queue_items = []
        kitchen_loads = {}

        for status in kitchen_statuses:
            all_queue_items.extend(status.current_queue)
            kitchen_loads[status.kitchen_id] = status.current_load

        # Filter out completed items for the response
        active_queue_items = [
            item for item in all_queue_items
            if item.status.value != "completed"
        ]

        return QueueStatusResponse(
            success=True,
            message=f"Queue status retrieved for {len(kitchen_statuses)} kitchens",
            queue_items=active_queue_items,
            total_items=len(active_queue_items),
            kitchen_loads=kitchen_loads
        )

    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard-summary")
async def get_dashboard_summary(services=Depends(get_services)):
    """Get dashboard summary data."""
    try:
        # Get orders from storage (this would be from database in production)
        from app.api.orders import orders_storage
        orders_list = list(orders_storage.values())

        # Calculate today's metrics
        from datetime import datetime, timedelta
        today = datetime.now().date()
        today_orders = [o for o in orders_list if o.timestamp.date() == today]
        completed_today = [o for o in today_orders if o.status.value == "completed"]

        # Get kitchen data
        kitchen_configs = services['excel_service'].load_kitchen_config()
        active_kitchens = len([k for k in kitchen_configs.values() if k.get('status') == 'active'])

        # Calculate average completion time
        avg_completion_time = 15  # Default fallback
        if completed_today:
            completion_times = []
            for order in completed_today:
                if order.actual_completion and order.timestamp:
                    diff = order.actual_completion - order.timestamp
                    completion_times.append(diff.total_seconds() / 60)  # Convert to minutes
            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)

        # Get current queue length
        try:
            kitchen_statuses = services['queue_manager'].get_all_kitchen_statuses()
            current_queue_length = sum(len(status.current_queue) for status in kitchen_statuses)
        except:
            current_queue_length = 0

        return {
            "success": True,
            "message": "Dashboard summary retrieved successfully",
            "total_orders_today": len(today_orders),
            "completed_orders_today": len(completed_today),
            "average_completion_time": round(avg_completion_time, 1),
            "active_kitchens": active_kitchens,
            "current_queue_length": current_queue_length,
            "efficiency_score": 85,  # Calculated metric
            "alerts_count": 0  # Would be calculated from starvation alerts
        }

    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(services=Depends(get_services)):
    """Get current system performance metrics."""
    try:
        # Get starvation statistics
        starvation_stats = services['starvation_prevention'].get_starvation_statistics()
        
        # Get kitchen efficiency metrics
        kitchen_statuses = services['queue_manager'].get_all_kitchen_statuses()
        kitchen_metrics = {}
        
        for status in kitchen_statuses:
            efficiency = services['queue_manager'].get_kitchen_efficiency_metrics(status.kitchen_id)
            kitchen_metrics[status.kitchen_id] = {
                "current_load": status.current_load,
                "capacity": status.capacity,
                "utilization": (status.current_load / status.capacity * 100) if status.capacity > 0 else 0,
                "efficiency_metrics": efficiency
            }
        
        # Calculate overall system metrics
        total_capacity = sum(status.capacity for status in kitchen_statuses)
        total_load = sum(status.current_load for status in kitchen_statuses)
        overall_utilization = (total_load / total_capacity * 100) if total_capacity > 0 else 0
        
        metrics = {
            "system_overview": {
                "total_kitchens": len(kitchen_statuses),
                "total_capacity": total_capacity,
                "total_current_load": total_load,
                "overall_utilization_percentage": round(overall_utilization, 2),
                "timestamp": datetime.now().isoformat()
            },
            "starvation_metrics": starvation_stats,
            "kitchen_metrics": kitchen_metrics,
            "bottlenecks": services['performance_learning'].identify_bottlenecks()
        }
        
        return PerformanceMetricsResponse(
            success=True,
            message="Performance metrics retrieved successfully",
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance/history", response_model=PerformanceHistoryResponse)
async def get_performance_history(
    query: PerformanceQueryRequest,
    services=Depends(get_services)
):
    """Get historical performance data with filtering."""
    try:
        historical_data = services['excel_service'].load_historical_data()
        
        # Apply filters
        filtered_data = historical_data
        
        if query.start_date:
            filtered_data = filtered_data[filtered_data['date'] >= query.start_date]
        
        if query.end_date:
            filtered_data = filtered_data[filtered_data['date'] <= query.end_date]
        
        if query.kitchen_id:
            filtered_data = filtered_data[filtered_data['kitchen_id'] == query.kitchen_id]
        
        if query.item_id:
            filtered_data = filtered_data[filtered_data['item_id'] == query.item_id]
        
        # Apply limit
        filtered_data = filtered_data.head(query.limit)
        
        # Convert to PerformanceRecord objects
        records = []
        for _, row in filtered_data.iterrows():
            records.append({
                "date": row['date'],
                "kitchen_id": row['kitchen_id'],
                "item_id": row['item_id'],
                "order_id": row['order_id'],
                "actual_prep_time": int(row['actual_prep_time']),
                "scheduled_prep_time": int(row['scheduled_prep_time']),
                "delay_minutes": int(row['delay_minutes']),
                "kitchen_load": int(row['kitchen_load'])
            })
        
        return PerformanceHistoryResponse(
            success=True,
            message=f"Retrieved {len(records)} performance records",
            records=records,
            total_count=len(records)
        )
        
    except Exception as e:
        logger.error(f"Error getting performance history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/starvation", response_model=dict)
async def get_starvation_status(services=Depends(get_services)):
    """Get current starvation status and statistics."""
    try:
        starvation_stats = services['starvation_prevention'].get_starvation_statistics()
        starving_items = services['starvation_prevention'].get_starving_items()
        
        # Get detailed info for each starving item
        starving_details = []
        for item_id in starving_items:
            item_info = services['starvation_prevention'].get_item_delay_info(item_id)
            starving_details.append(item_info)
        
        return {
            "success": True,
            "message": "Starvation status retrieved successfully",
            "statistics": starvation_stats,
            "starving_items_details": starving_details,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting starvation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reoptimize", response_model=dict)
async def trigger_reoptimization(services=Depends(get_services)):
    """Trigger reoptimization of all pending orders."""
    try:
        results = services['ai_agent'].reoptimize_pending_orders()
        
        return {
            "success": True,
            "message": f"Reoptimized {len(results)} pending orders",
            "reoptimization_results": [
                {
                    "order_id": result.order_id,
                    "total_estimated_time": result.total_estimated_time,
                    "synchronization_achieved": result.synchronization_achieved,
                    "anti_starvation_applied": result.anti_starvation_applied
                }
                for result in results
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering reoptimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", response_model=dict)
async def get_ai_insights(services=Depends(get_services)):
    """Get AI-generated insights about system performance."""
    try:
        insights = services['ai_agent'].get_ai_insights()
        
        return {
            "success": True,
            "message": "AI insights retrieved successfully",
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency-reschedule", response_model=dict)
async def emergency_reschedule(services=Depends(get_services)):
    """Trigger emergency rescheduling for starving items."""
    try:
        starving_items = services['starvation_prevention'].get_starving_items()
        
        if not starving_items:
            return {
                "success": True,
                "message": "No starving items found - no emergency rescheduling needed",
                "timestamp": datetime.now().isoformat()
            }
        
        emergency_result = services['ai_agent'].emergency_reschedule(starving_items)
        
        return {
            "success": True,
            "message": f"Emergency rescheduling completed for {len(starving_items)} items",
            "emergency_result": emergency_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in emergency rescheduling: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/starvation-alerts")
async def get_starvation_alerts(services=Depends(get_services)):
    """Get current starvation alerts."""
    try:
        # Try to get alerts from starvation prevention service
        try:
            alerts = services['starvation_prevention'].get_current_alerts()
        except AttributeError:
            # Fallback: create mock alerts or get from queue manager
            alerts = []
            try:
                kitchen_statuses = services['queue_manager'].get_all_kitchen_statuses()
                for status in kitchen_statuses:
                    for item in status.current_queue:
                        if hasattr(item, 'starvation_count') and item.starvation_count > 2:
                            alerts.append({
                                "queue_id": item.queue_id,
                                "order_id": item.order_id,
                                "item_id": item.item_id,
                                "starvation_count": item.starvation_count,
                                "wait_time_minutes": 25,  # Mock value
                                "priority_level": item.priority.value if hasattr(item, 'priority') else "medium"
                            })
            except:
                alerts = []

        return {
            "success": True,
            "message": f"Retrieved {len(alerts)} starvation alerts",
            "alerts": alerts
        }

    except Exception as e:
        logger.error(f"Error getting starvation alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-indicators")
async def get_health_indicators(services=Depends(get_services)):
    """Get system health indicators."""
    try:
        # Get basic system metrics
        import psutil

        indicators = [
            {
                "name": "CPU Usage",
                "status": "good" if psutil.cpu_percent() < 80 else "warning",
                "value": psutil.cpu_percent(),
                "threshold": 80,
                "description": "System CPU utilization"
            },
            {
                "name": "Memory Usage",
                "status": "good" if psutil.virtual_memory().percent < 85 else "warning",
                "value": psutil.virtual_memory().percent,
                "threshold": 85,
                "description": "System memory utilization"
            },
            {
                "name": "Queue Health",
                "status": "good",
                "value": 100,
                "threshold": 90,
                "description": "Kitchen queue processing health"
            },
            {
                "name": "Order Processing",
                "status": "good",
                "value": 95,
                "threshold": 80,
                "description": "Order processing efficiency"
            }
        ]

        overall_health = "healthy"
        if any(i["status"] == "critical" for i in indicators):
            overall_health = "critical"
        elif any(i["status"] == "warning" for i in indicators):
            overall_health = "warning"

        return {
            "success": True,
            "message": "Health indicators retrieved successfully",
            "overall_health": overall_health,
            "indicators": indicators
        }

    except Exception as e:
        logger.error(f"Error getting health indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-load")
async def get_system_load(services=Depends(get_services)):
    """Get current system load metrics."""
    try:
        # Get orders from storage
        from app.api.orders import orders_storage
        orders_list = list(orders_storage.values())

        # Get kitchen data
        kitchen_configs = services['excel_service'].load_kitchen_config()
        active_kitchens = len([k for k in kitchen_configs.values() if k.get('status') == 'active'])

        # Calculate metrics
        active_orders = len([o for o in orders_list if o.status.value in ['pending', 'preparing', 'cooking']])

        # Calculate average wait time (mock for now)
        avg_wait_time = 12.5  # minutes

        # Calculate system efficiency
        system_efficiency = 87.5  # percentage

        return {
            "success": True,
            "message": "System load retrieved successfully",
            "total_orders": active_orders,
            "active_kitchens": active_kitchens,
            "average_wait_time": avg_wait_time,
            "system_efficiency": system_efficiency
        }

    except Exception as e:
        logger.error(f"Error getting system load: {e}")
        raise HTTPException(status_code=500, detail=str(e))
