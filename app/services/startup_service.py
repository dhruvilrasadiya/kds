"""
Startup service for initializing the Smart Kitchen Queue Management System.
This service handles data migration from Excel to MongoDB on startup.
"""

import logging
from typing import Dict, Any
import asyncio

from app.services.mongodb_service import mongodb_service
from app.services.excel_service import ExcelDataService
from app.services.data_sync_service import DataSyncService

logger = logging.getLogger(__name__)


class StartupService:
    """Service to handle application startup and data initialization."""
    
    def __init__(self):
        self.mongodb_service = mongodb_service
        self.excel_service = ExcelDataService()
        self.data_sync_service = DataSyncService()
        
    async def initialize_application(self) -> Dict[str, Any]:
        """Initialize the application with data migration and setup."""
        logger.info("🚀 Starting Smart Kitchen Queue Management System initialization...")
        
        results = {
            "mongodb_connection": False,
            "data_migration": False,
            "menu_items_count": 0,
            "kitchens_count": 0,
            "errors": []
        }
        
        try:
            # Step 1: Connect to MongoDB
            logger.info("📡 Connecting to MongoDB...")
            await self.mongodb_service.connect()
            
            # Check if MongoDB is connected
            health = await self.mongodb_service.health_check()
            if health["status"] == "connected":
                results["mongodb_connection"] = True
                logger.info("✅ MongoDB connected successfully")
            else:
                logger.warning("⚠️ MongoDB not connected, using fallback storage")
                results["errors"].append("MongoDB connection failed")
            
            # Step 2: Check if data already exists in MongoDB
            existing_items = await self.mongodb_service.get_menu_items()
            existing_kitchens = await self.mongodb_service.get_kitchens()
            
            if existing_items and existing_kitchens:
                logger.info(f"📊 Found existing data: {len(existing_items)} items, {len(existing_kitchens)} kitchens")
                results["menu_items_count"] = len(existing_items)
                results["kitchens_count"] = len(existing_kitchens)
                results["data_migration"] = True
            else:
                # Step 3: Migrate data from Excel to MongoDB
                logger.info("📋 No existing data found, migrating from Excel...")
                migration_result = await self._migrate_excel_to_mongodb()
                
                if migration_result["success"]:
                    results["data_migration"] = True
                    results["menu_items_count"] = migration_result["menu_items_count"]
                    results["kitchens_count"] = migration_result["kitchens_count"]
                    logger.info("✅ Data migration completed successfully")
                else:
                    results["errors"].extend(migration_result["errors"])
                    logger.error("❌ Data migration failed")
            
            # Step 4: Validate data integrity
            await self._validate_data_integrity()
            
            logger.info("🎉 Application initialization completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"💥 Critical error during initialization: {e}")
            results["errors"].append(f"Initialization error: {str(e)}")
            return results
    
    async def _migrate_excel_to_mongodb(self) -> Dict[str, Any]:
        """Migrate data from Excel to MongoDB."""
        migration_result = {
            "success": False,
            "menu_items_count": 0,
            "kitchens_count": 0,
            "errors": []
        }
        
        try:
            # Sync all data from Excel to MongoDB
            sync_results = await self.data_sync_service.sync_all_data()
            
            if sync_results.get("menu_items", False):
                # Count migrated items
                items = await self.mongodb_service.get_menu_items()
                migration_result["menu_items_count"] = len(items)
                logger.info(f"✅ Migrated {len(items)} menu items")
            else:
                migration_result["errors"].append("Failed to migrate menu items")
                
            if sync_results.get("kitchens", False):
                # Count migrated kitchens
                kitchens = await self.mongodb_service.get_kitchens()
                migration_result["kitchens_count"] = len(kitchens)
                logger.info(f"✅ Migrated {len(kitchens)} kitchens")
            else:
                migration_result["errors"].append("Failed to migrate kitchens")
            
            # Consider migration successful if at least one type succeeded
            migration_result["success"] = (
                sync_results.get("menu_items", False) or 
                sync_results.get("kitchens", False)
            )
            
            return migration_result
            
        except Exception as e:
            logger.error(f"Error during data migration: {e}")
            migration_result["errors"].append(f"Migration error: {str(e)}")
            return migration_result
    
    async def _validate_data_integrity(self):
        """Validate that essential data is available."""
        try:
            # Check menu items
            items = await self.mongodb_service.get_menu_items()
            if not items:
                logger.warning("⚠️ No menu items found in database")
            else:
                # Validate item structure
                for item in items[:3]:  # Check first 3 items
                    required_fields = ["item_id", "item_name", "kitchen_id", "prep_time_minutes"]
                    missing_fields = [field for field in required_fields if field not in item]
                    if missing_fields:
                        logger.warning(f"⚠️ Item {item.get('item_id', 'unknown')} missing fields: {missing_fields}")
            
            # Check kitchens
            kitchens = await self.mongodb_service.get_kitchens()
            if not kitchens:
                logger.warning("⚠️ No kitchens found in database")
            else:
                logger.info(f"✅ Data validation passed: {len(items)} items, {len(kitchens)} kitchens")
                
        except Exception as e:
            logger.error(f"Error during data validation: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            # MongoDB health
            mongodb_health = await self.mongodb_service.health_check()
            
            # Data counts
            items_count = len(await self.mongodb_service.get_menu_items())
            kitchens_count = len(await self.mongodb_service.get_kitchens())
            orders_count = len(await self.mongodb_service.get_orders())
            queue_items_count = len(await self.mongodb_service.get_queue_items())
            
            return {
                "status": "healthy" if mongodb_health["status"] == "connected" else "degraded",
                "mongodb": mongodb_health,
                "data_counts": {
                    "menu_items": items_count,
                    "kitchens": kitchens_count,
                    "orders": orders_count,
                    "queue_items": queue_items_count
                },
                "timestamp": "now"
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "now"
            }


# Global startup service instance
startup_service = StartupService()
