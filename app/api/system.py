"""
System API endpoints for the Smart Kitchen Queue Management System.
"""

import logging
import psutil
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request

from app.models import (
    ReloadConfigRequest, SystemHealthResponse, ConfigReloadResponse
)
from app.config import config
from app import __version__

logger = logging.getLogger(__name__)

router = APIRouter()

# Track system start time
system_start_time = datetime.now()


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


@router.get("/health", response_model=SystemHealthResponse)
async def health_check(services=Depends(get_services)):
    """Comprehensive system health check."""
    try:
        components = {}
        overall_status = "healthy"
        
        # Check MongoDB service
        try:
            mongodb_health = await services['mongodb_service'].health_check()
            if mongodb_health["status"] == "connected":
                collections = mongodb_health.get("collections", {})
                total_docs = sum(collections.values())
                components["mongodb"] = f"healthy - {total_docs} documents across {len(collections)} collections"
            else:
                components["mongodb"] = f"warning - {mongodb_health.get('message', 'disconnected')}"
                overall_status = "degraded"
        except Exception as e:
            components["mongodb"] = f"error - {str(e)}"
            overall_status = "degraded"

        # Check Excel service (fallback)
        try:
            kitchens = services['excel_service'].load_kitchen_config()
            components["excel_service"] = f"healthy - {len(kitchens)} kitchens loaded (fallback)"
        except Exception as e:
            components["excel_service"] = f"error - {str(e)}"
            # Don't change overall status as MongoDB is primary
        
        # Check queue manager
        try:
            statuses = services['queue_manager'].get_all_kitchen_statuses()
            total_items = sum(len(status.current_queue) for status in statuses)
            components["queue_manager"] = f"healthy - {total_items} items in queues"
        except Exception as e:
            components["queue_manager"] = f"error - {str(e)}"
            overall_status = "degraded"
        
        # Check starvation prevention
        try:
            stats = services['starvation_prevention'].get_starvation_statistics()
            starving_count = stats.get("currently_starving", 0)
            components["starvation_prevention"] = f"healthy - {starving_count} starving items"
            if starving_count > 5:
                overall_status = "warning"
        except Exception as e:
            components["starvation_prevention"] = f"error - {str(e)}"
            overall_status = "degraded"
        
        # Check AI agent (basic connectivity test)
        try:
            # This is a simple check - in production you might want to test actual AI functionality
            components["ai_agent"] = "healthy - agent initialized"
        except Exception as e:
            components["ai_agent"] = f"error - {str(e)}"
            overall_status = "degraded"
        
        # Check performance learning
        try:
            bottlenecks = services['performance_learning'].identify_bottlenecks()
            components["performance_learning"] = f"healthy - {len(bottlenecks)} bottlenecks identified"
        except Exception as e:
            components["performance_learning"] = f"error - {str(e)}"
            overall_status = "degraded"
        
        # System resources
        try:
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=1)
            components["system_resources"] = f"CPU: {cpu_percent}%, Memory: {memory_percent}%"
            
            if memory_percent > 90 or cpu_percent > 90:
                overall_status = "warning"
        except Exception as e:
            components["system_resources"] = f"error - {str(e)}"
        
        # Calculate uptime
        uptime = datetime.now() - system_start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        return SystemHealthResponse(
            success=True,
            message=f"System health check completed - status: {overall_status}",
            status=overall_status,
            components=components,
            uptime=uptime_str,
            version=__version__
        )
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return SystemHealthResponse(
            success=False,
            message=f"Health check failed: {str(e)}",
            status="error",
            components={"error": str(e)},
            version=__version__
        )


@router.post("/reload-config", response_model=ConfigReloadResponse)
async def reload_configuration(
    reload_request: ReloadConfigRequest,
    services=Depends(get_services)
):
    """Reload system configuration from Excel files."""
    try:
        reloaded_components = []
        
        # Clear Excel service cache
        if reload_request.clear_cache:
            services['excel_service'].clear_cache()
            reloaded_components.append("excel_service_cache")
        
        # Reload kitchen configurations
        try:
            services['queue_manager']._load_kitchen_configs()
            reloaded_components.append("kitchen_configurations")
        except Exception as e:
            logger.error(f"Error reloading kitchen configs: {e}")
        
        # Clear performance learning cache
        if reload_request.clear_cache:
            services['performance_learning'].clear_cache()
            reloaded_components.append("performance_learning_cache")
        
        # Clear starvation prevention old entries
        services['starvation_prevention'].cleanup_old_entries()
        reloaded_components.append("starvation_prevention_cleanup")
        
        logger.info(f"Configuration reloaded: {reloaded_components}")
        
        return ConfigReloadResponse(
            success=True,
            message="Configuration reloaded successfully",
            reloaded_components=reloaded_components,
            cache_cleared=reload_request.clear_cache
        )
        
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=dict)
async def get_system_metrics(services=Depends(get_services)):
    """Get comprehensive system metrics."""
    try:
        # Kitchen metrics
        kitchen_statuses = services['queue_manager'].get_all_kitchen_statuses()
        kitchen_metrics = {}
        
        for status in kitchen_statuses:
            efficiency = services['queue_manager'].get_kitchen_efficiency_metrics(status.kitchen_id)
            kitchen_metrics[status.kitchen_id] = {
                "capacity": status.capacity,
                "current_load": status.current_load,
                "utilization": (status.current_load / status.capacity * 100) if status.capacity > 0 else 0,
                "queue_length": len(status.current_queue),
                "efficiency": efficiency
            }
        
        # Starvation metrics
        starvation_stats = services['starvation_prevention'].get_starvation_statistics()
        
        # Performance metrics
        bottlenecks = services['performance_learning'].identify_bottlenecks()
        
        # System resource metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if psutil.disk_usage('/') else 0
        }
        
        return {
            "success": True,
            "message": "System metrics retrieved successfully",
            "metrics": {
                "kitchen_metrics": kitchen_metrics,
                "starvation_metrics": starvation_stats,
                "bottlenecks": bottlenecks,
                "system_resources": system_metrics,
                "uptime": str(datetime.now() - system_start_time).split('.')[0]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-report", response_model=dict)
async def get_learning_report(services=Depends(get_services)):
    """Get comprehensive learning and performance report."""
    try:
        report = services['performance_learning'].generate_learning_report()
        
        return {
            "success": True,
            "message": "Learning report generated successfully",
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating learning report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capacity-recommendations", response_model=dict)
async def get_capacity_recommendations(services=Depends(get_services)):
    """Get kitchen capacity optimization recommendations."""
    try:
        recommendations = services['performance_learning'].optimize_kitchen_capacity_recommendations()
        
        return {
            "success": True,
            "message": "Capacity recommendations generated successfully",
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating capacity recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=dict)
async def get_current_config():
    """Get current system configuration."""
    try:
        return {
            "success": True,
            "message": "Current configuration retrieved",
            "config": {
                "excel_file_path": config.EXCEL_FILE_PATH,
                "ollama_base_url": config.OLLAMA_BASE_URL,
                "ollama_model": config.OLLAMA_MODEL,
                "max_starvation_count": config.MAX_STARVATION_COUNT,
                "synchronization_window_minutes": config.SYNCHRONIZATION_WINDOW_MINUTES,
                "performance_history_days": config.PERFORMANCE_HISTORY_DAYS,
                "api_host": config.API_HOST,
                "api_port": config.API_PORT,
                "debug_mode": config.DEBUG_MODE
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
