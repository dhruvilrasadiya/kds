"""
FastAPI main application for the Smart Kitchen Queue Management System.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import config
from app.services.excel_service import ExcelDataService
from app.services.mongodb_service import mongodb_service
from app.services.data_sync_service import data_sync_service
from app.services.startup_service import startup_service
from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.services.ai_agent import KitchenAIAgent
from app.services.performance_learning import PerformanceLearning
from app.api import orders, kitchens, realtime, system, menu, queue

logger = logging.getLogger(__name__)

# Global service instances
excel_service = None
mongodb_service_instance = None
data_sync_service_instance = None
queue_manager = None
starvation_prevention = None
ai_agent = None
performance_learning = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global excel_service, mongodb_service_instance, data_sync_service_instance, queue_manager, starvation_prevention, ai_agent, performance_learning

    try:
        # Initialize application using startup service
        logger.info("🚀 Initializing Smart Kitchen Queue Management System...")

        # Run comprehensive initialization
        init_results = await startup_service.initialize_application()

        if init_results["errors"]:
            logger.warning(f"⚠️ Initialization completed with warnings: {init_results['errors']}")
        else:
            logger.info("✅ Application initialization completed successfully")

        # Initialize service instances
        mongodb_service_instance = mongodb_service
        excel_service = ExcelDataService()
        data_sync_service_instance = data_sync_service

        # Initialize queue and AI services (these will use MongoDB exclusively)
        queue_manager = KitchenQueueManager()  # No longer needs excel_service
        starvation_prevention = StarvationPrevention()
        performance_learning = PerformanceLearning(excel_service)  # Keep for now, will update later
        ai_agent = KitchenAIAgent(excel_service, queue_manager, starvation_prevention, performance_learning)

        # Store services in app state
        app.state.excel_service = excel_service
        app.state.mongodb_service = mongodb_service_instance
        app.state.data_sync_service = data_sync_service_instance
        app.state.startup_service = startup_service
        app.state.queue_manager = queue_manager
        app.state.starvation_prevention = starvation_prevention
        app.state.ai_agent = ai_agent
        app.state.performance_learning = performance_learning

        logger.info(f"🎉 All services initialized successfully! Data: {init_results['menu_items_count']} items, {init_results['kitchens_count']} kitchens")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup MongoDB connection
        if mongodb_service_instance:
            await mongodb_service_instance.disconnect()
        logger.info("Shutting down Smart Kitchen Queue Management System")


# Create FastAPI application
app = FastAPI(
    title="Smart Kitchen Queue Management System",
    description="An intelligent kitchen queue management system with AI-driven optimization",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": 500
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Smart Kitchen Queue Management System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/system/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# Include API routers
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(kitchens.router, prefix="/api/kitchens", tags=["Kitchens"])
app.include_router(queue.router, prefix="/api/queue", tags=["Queue"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["Real-time"])
app.include_router(system.router, prefix="/api/system", tags=["System"])
app.include_router(menu.router, prefix="/api/menu", tags=["Menu"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG_MODE
    )
