"""
Data synchronization service between Excel and MongoDB.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from app.services.excel_service import ExcelDataService
from app.services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)


class DataSyncService:
    """Service to synchronize data between Excel and MongoDB."""
    
    def __init__(self):
        self.excel_service = ExcelDataService()
        self.mongodb_service = mongodb_service
        
    async def sync_all_data(self) -> Dict[str, bool]:
        """Sync all data from Excel to MongoDB."""
        results = {
            "menu_items": False,
            "kitchens": False
        }
        
        try:
            # Sync menu items
            results["menu_items"] = await self.sync_menu_items()
            
            # Sync kitchens
            results["kitchens"] = await self.sync_kitchens()
            
            logger.info(f"Data sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error during data sync: {e}")
            return results
    
    async def sync_menu_items(self) -> bool:
        """Sync menu items from Excel to MongoDB."""
        try:
            # Load menu items from Excel - this returns a dictionary, not DataFrame
            menu_items_dict = self.excel_service.load_menu_items()

            if not menu_items_dict:
                logger.warning("No menu items found in Excel")
                return False

            # Convert dictionary to list of dictionaries for MongoDB
            menu_items = []
            for item_id, item_data in menu_items_dict.items():
                item = {
                    "item_id": item_id,
                    "name": item_data.get("name", ""),
                    "description": item_data.get("description", ""),
                    "price": float(item_data.get("price", 0)),
                    "prep_time": int(item_data.get("prep_time", 15)),
                    "difficulty": item_data.get("difficulty", "medium"),
                    "category": item_data.get("category", "main"),
                    "image_url": item_data.get("image_url", ""),
                    "calories": int(item_data.get("calories", 0)),
                    "available": bool(item_data.get("available", True)),
                    "ingredients": item_data.get("ingredients", []) if isinstance(item_data.get("ingredients"), list) else item_data.get("ingredients", "").split(",") if item_data.get("ingredients") else [],
                    "allergens": item_data.get("allergens", []) if isinstance(item_data.get("allergens"), list) else item_data.get("allergens", "").split(",") if item_data.get("allergens") else [],
                    "nutritional_info": {
                        "calories": int(item_data.get("calories", 0)),
                        "protein": item_data.get("protein", ""),
                        "carbs": item_data.get("carbs", ""),
                        "fat": item_data.get("fat", "")
                    },
                    "sync_source": "excel",
                    "synced_at": datetime.now()
                }
                menu_items.append(item)
            
            # Upsert to MongoDB
            success = await self.mongodb_service.upsert_menu_items(menu_items)
            
            if success:
                logger.info(f"Synced {len(menu_items)} menu items to MongoDB")
            else:
                logger.error("Failed to sync menu items to MongoDB")
                
            return success
            
        except Exception as e:
            logger.error(f"Error syncing menu items: {e}")
            return False
    
    async def sync_kitchens(self) -> bool:
        """Sync kitchens from Excel to MongoDB."""
        try:
            # Load kitchen config from Excel
            kitchen_config = self.excel_service.load_kitchen_config()
            
            if not kitchen_config:
                logger.warning("No kitchen config found in Excel")
                return False
            
            # Convert to list of dictionaries
            kitchens = []
            for kitchen_id, config in kitchen_config.items():
                kitchen = {
                    "kitchen_id": kitchen_id,
                    "kitchen_name": config.get("kitchen_name", config.get("name", kitchen_id)),
                    "name": config.get("kitchen_name", config.get("name", kitchen_id)),
                    "capacity": int(config.get("capacity", 1)),
                    "specialization": config.get("specialization", "general"),
                    "status": config.get("status", "active"),
                    "current_load": int(config.get("current_load", 0)),
                    "staff_count": int(config.get("staff_count", 1)),
                    "equipment": config.get("equipment", "").split(",") if config.get("equipment") else [],
                    "sync_source": "excel",
                    "synced_at": datetime.now()
                }
                kitchens.append(kitchen)
            
            # Upsert to MongoDB
            success = await self.mongodb_service.upsert_kitchens(kitchens)
            
            if success:
                logger.info(f"Synced {len(kitchens)} kitchens to MongoDB")
            else:
                logger.error("Failed to sync kitchens to MongoDB")
                
            return success
            
        except Exception as e:
            logger.error(f"Error syncing kitchens: {e}")
            return False
    
    async def get_menu_items(self, category: Optional[str] = None, available_only: bool = True) -> List[Dict]:
        """Get menu items from MongoDB with fallback to Excel."""
        try:
            # Try MongoDB first
            items = await self.mongodb_service.get_menu_items(category, available_only)
            
            if items:
                return items
            
            # Fallback to Excel and sync
            logger.info("No items in MongoDB, syncing from Excel")
            await self.sync_menu_items()
            
            # Try MongoDB again
            return await self.mongodb_service.get_menu_items(category, available_only)
            
        except Exception as e:
            logger.error(f"Error getting menu items: {e}")
            return []
    
    async def get_menu_item(self, item_id: str) -> Optional[Dict]:
        """Get a specific menu item from MongoDB with fallback to Excel."""
        try:
            # Try MongoDB first
            item = await self.mongodb_service.get_menu_item(item_id)
            
            if item:
                return item
            
            # Fallback to Excel and sync
            logger.info(f"Item {item_id} not found in MongoDB, syncing from Excel")
            await self.sync_menu_items()
            
            # Try MongoDB again
            return await self.mongodb_service.get_menu_item(item_id)
            
        except Exception as e:
            logger.error(f"Error getting menu item {item_id}: {e}")
            return None
    
    async def get_kitchens(self) -> List[Dict]:
        """Get kitchens from MongoDB with fallback to Excel."""
        try:
            # Try MongoDB first
            kitchens = await self.mongodb_service.get_kitchens()
            
            if kitchens:
                return kitchens
            
            # Fallback to Excel and sync
            logger.info("No kitchens in MongoDB, syncing from Excel")
            await self.sync_kitchens()
            
            # Try MongoDB again
            return await self.mongodb_service.get_kitchens()
            
        except Exception as e:
            logger.error(f"Error getting kitchens: {e}")
            return []
    
    async def validate_order_items(self, item_ids: List[str]) -> Dict[str, bool]:
        """Validate that order items exist and are available."""
        validation_results = {}
        
        try:
            for item_id in item_ids:
                item = await self.get_menu_item(item_id)
                validation_results[item_id] = (
                    item is not None and 
                    item.get("available", False)
                )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating order items: {e}")
            return {item_id: False for item_id in item_ids}
    
    async def create_order(self, order_data: Dict) -> Optional[str]:
        """Create order in MongoDB."""
        try:
            # Validate items first
            item_ids = order_data.get("items", [])
            validation_results = await self.validate_order_items(item_ids)
            
            invalid_items = [item_id for item_id, valid in validation_results.items() if not valid]
            if invalid_items:
                logger.error(f"Invalid items in order: {invalid_items}")
                return None
            
            # Create order in MongoDB
            return await self.mongodb_service.create_order(order_data)
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    async def get_orders(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get orders from MongoDB."""
        try:
            return await self.mongodb_service.get_orders(status, limit)
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status in MongoDB."""
        try:
            return await self.mongodb_service.update_order_status(order_id, status)
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False
    
    async def health_check(self) -> Dict:
        """Check health of data sync service."""
        try:
            mongodb_health = await self.mongodb_service.health_check()
            
            return {
                "status": "healthy" if mongodb_health["status"] == "connected" else "degraded",
                "mongodb": mongodb_health,
                "excel_service": "available"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Global data sync service instance
data_sync_service = DataSyncService()
