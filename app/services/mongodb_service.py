"""
MongoDB service for the Smart Kitchen Queue Management System.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, ConnectionFailure
import asyncio

logger = logging.getLogger(__name__)


class MongoDBService:
    """MongoDB service for data persistence."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._connection_string = os.getenv(
            "MONGODB_URL", 
            "mongodb://admin:password123@localhost:27017/smart_kitchen"
        )
        self._database_name = os.getenv("MONGODB_DATABASE", "smart_kitchen")
        self._connected = False  # Add connection status flag
        
    async def connect(self):
        """Connect to MongoDB."""
        try:
            logger.info(f"Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(self._connection_string)
            self.db = self.client[self._database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            self._connected = True
            logger.info(f"Connected to MongoDB: {self._database_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except ConnectionFailure as e:
            logger.warning(f"Failed to connect to MongoDB: {e}")
            logger.info("Falling back to in-memory storage")
            # Fallback to in-memory storage
            self.client = None
            self.db = None
            self._connected = False
            self._init_fallback_storage()
        except Exception as e:
            logger.warning(f"MongoDB connection error: {e}")
            logger.info("Falling back to in-memory storage")
            self.client = None
            self.db = None
            self._connected = False
            self._init_fallback_storage()

    def _init_fallback_storage(self):
        """Initialize in-memory fallback storage."""
        self._fallback_storage = {
            "menu_items": {},
            "kitchens": {},
            "orders": {},
            "queue_items": {}
        }
            
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client is not None:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
            
    async def _create_indexes(self):
        """Create database indexes."""
        if not self._connected or self.db is None:
            return
            
        try:
            # Menu items indexes
            await self.db.menu_items.create_index("item_id", unique=True)
            await self.db.menu_items.create_index("category")
            await self.db.menu_items.create_index("available")
            
            # Kitchen indexes
            await self.db.kitchens.create_index("kitchen_id", unique=True)
            await self.db.kitchens.create_index("status")
            
            # Orders indexes
            await self.db.orders.create_index("order_id", unique=True)
            await self.db.orders.create_index("status")
            await self.db.orders.create_index("timestamp")
            
            # Queue items indexes
            await self.db.queue_items.create_index("queue_id", unique=True)
            await self.db.queue_items.create_index("order_id")
            await self.db.queue_items.create_index("kitchen_id")
            await self.db.queue_items.create_index("status")
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # Menu Items Operations
    async def get_menu_items(self, category: Optional[str] = None, available_only: bool = True) -> List[Dict]:
        """Get menu items."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            items = list(self._fallback_storage["menu_items"].values())

            # Apply filters
            if available_only:
                items = [item for item in items if item.get("available", True)]
            if category:
                items = [item for item in items if item.get("category") == category]

            return items

        try:
            filter_query = {}
            if category:
                filter_query["category"] = category
            if available_only:
                filter_query["available"] = True

            cursor = self.db.menu_items.find(filter_query)
            items = await cursor.to_list(length=None)

            # Convert ObjectId to string and ensure field compatibility
            for item in items:
                item["_id"] = str(item["_id"])
                # Ensure both field name formats for compatibility
                if "item_name" in item and "name" not in item:
                    item["name"] = item["item_name"]
                if "prep_time_minutes" in item and "prep_time" not in item:
                    item["prep_time"] = item["prep_time_minutes"]

            return items

        except Exception as e:
            logger.error(f"Error getting menu items: {e}")
            return []
    
    async def get_menu_item(self, item_id: str) -> Optional[Dict]:
        """Get a specific menu item."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            return self._fallback_storage["menu_items"].get(item_id)

        try:
            item = await self.db.menu_items.find_one({"item_id": item_id})
            if item:
                item["_id"] = str(item["_id"])
                # Ensure field compatibility
                if "item_name" in item and "name" not in item:
                    item["name"] = item["item_name"]
                if "prep_time_minutes" in item and "prep_time" not in item:
                    item["prep_time"] = item["prep_time_minutes"]
            return item

        except Exception as e:
            logger.error(f"Error getting menu item {item_id}: {e}")
            return None
    
    async def upsert_menu_items(self, items: List[Dict]) -> bool:
        """Insert or update menu items."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            for item in items:
                item["updated_at"] = datetime.now()
                self._fallback_storage["menu_items"][item["item_id"]] = item
            logger.info(f"Upserted {len(items)} menu items to fallback storage")
            return True

        try:
            operations = []
            for item in items:
                # Add timestamp
                item["updated_at"] = datetime.now()

                operations.append({
                    "replaceOne": {
                        "filter": {"item_id": item["item_id"]},
                        "replacement": item,
                        "upsert": True
                    }
                })

            if operations:
                result = await self.db.menu_items.bulk_write(operations)
                logger.info(f"Upserted {result.upserted_count + result.modified_count} menu items")

            return True

        except Exception as e:
            logger.error(f"Error upserting menu items: {e}")
            return False

    async def validate_order_items(self, item_ids: List[str]) -> Dict[str, bool]:
        """Validate that all items exist and are available."""
        validation_results = {}

        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            for item_id in item_ids:
                item = self._fallback_storage["menu_items"].get(item_id)
                validation_results[item_id] = item is not None and item.get("available", True)
            return validation_results

        try:
            for item_id in item_ids:
                item = await self.db.menu_items.find_one({"item_id": item_id})
                validation_results[item_id] = item is not None and item.get("available", True)

            return validation_results

        except Exception as e:
            logger.error(f"Error validating order items: {e}")
            # Return all as invalid on error
            return {item_id: False for item_id in item_ids}

    # Kitchen Operations
    async def get_kitchens(self) -> List[Dict]:
        """Get all kitchens."""
        if not self._connected or self.db is None:
            return list(self._fallback_storage["kitchens"].values())
            
        try:
            cursor = self.db.kitchens.find({})
            kitchens = await cursor.to_list(length=None)
            
            for kitchen in kitchens:
                kitchen["_id"] = str(kitchen["_id"])
                
            return kitchens
            
        except Exception as e:
            logger.error(f"Error getting kitchens: {e}")
            return []
    
    async def upsert_kitchens(self, kitchens: List[Dict]) -> bool:
        """Insert or update kitchens."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            for kitchen in kitchens:
                kitchen["updated_at"] = datetime.now()
                self._fallback_storage["kitchens"][kitchen["kitchen_id"]] = kitchen
            logger.info(f"Upserted {len(kitchens)} kitchens to fallback storage")
            return True
            
        try:
            operations = []
            for kitchen in kitchens:
                kitchen["updated_at"] = datetime.now()
                
                operations.append({
                    "replaceOne": {
                        "filter": {"kitchen_id": kitchen["kitchen_id"]},
                        "replacement": kitchen,
                        "upsert": True
                    }
                })
            
            if operations:
                result = await self.db.kitchens.bulk_write(operations)
                logger.info(f"Upserted {result.upserted_count + result.modified_count} kitchens")
                
            return True
            
        except Exception as e:
            logger.error(f"Error upserting kitchens: {e}")
            return False
        
    def _serialize_order_data(self, order_data: Dict) -> Dict[str, Any]:
        """
        Serialize order data for MongoDB storage.
        Converts complex objects to MongoDB-compatible formats.
        """
        try:
            serialized = order_data.copy()
            
            # Handle queue_items serialization if present
            if "queue_items" in serialized and serialized["queue_items"]:
                queue_items_list = []
                for item in serialized["queue_items"]:
                    if hasattr(item, '__dict__'):
                        # Convert Pydantic model or custom object to dict
                        item_dict = item.__dict__ if hasattr(item, '__dict__') else item
                    else:
                        item_dict = item
                    
                    # Ensure datetime objects are properly handled
                    if isinstance(item_dict, dict):
                        for key, value in item_dict.items():
                            if isinstance(value, datetime):
                                item_dict[key] = value
                            elif hasattr(value, 'value'):  # Handle enums
                                item_dict[key] = value.value
                    
                    queue_items_list.append(item_dict)
                
                serialized["queue_items"] = queue_items_list
            
            # Handle datetime objects
            for key, value in serialized.items():
                if isinstance(value, datetime):
                    # Keep datetime objects as they are - MongoDB handles them natively
                    continue
                elif hasattr(value, 'value'):  # Handle enum values
                    serialized[key] = value.value
                elif hasattr(value, '__dict__'):  # Handle custom objects
                    serialized[key] = value.__dict__
            
            return serialized
            
        except Exception as e:
            logger.error(f"Error serializing order data: {e}")
            # Return original data if serialization fails
            return order_data
    
    # Order Operations
    async def create_order(self, order_data: Dict) -> Optional[str]:
        """Create a new order."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            order_data["created_at"] = datetime.now()
            order_data["updated_at"] = datetime.now()
            # Serialize for consistency even in fallback storage
            serialized_data = self._serialize_order_data(order_data)
            self._fallback_storage["orders"][order_data["order_id"]] = serialized_data
            logger.info(f"Created order in fallback storage: {order_data['order_id']}")
            return order_data["order_id"]
            
        try:
            order_data["created_at"] = datetime.now()
            order_data["updated_at"] = datetime.now()
            
            # Serialize the order data before inserting into MongoDB
            serialized_data = self._serialize_order_data(order_data)
            
            result = await self.db.orders.insert_one(serialized_data)
            logger.info(f"Created order: {order_data['order_id']}")
            
            return order_data["order_id"]
            
        except DuplicateKeyError:
            logger.error(f"Order {order_data['order_id']} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None

    
    async def get_orders(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get orders with optional status filter."""
        if not self._connected or self.db is None:
            print("Not connected to MongoDB, using fallback storage")
            # Fallback to in-memory storage
            orders = list(self._fallback_storage["orders"].values())
            if status:
                orders = [order for order in orders if order.get("status") == status]
            # Sort by timestamp (most recent first) and limit
            orders.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
            return orders[:limit]
            
        try:
            filter_query = {}
            print(f"Getting orders with status: {status}")
            if status:
                filter_query["status"] = status
                
            cursor = self.db.orders.find(filter_query).sort("timestamp", -1).limit(limit)
            orders = await cursor.to_list(length=None)
            
            for order in orders:
                order["_id"] = str(order["_id"])
                
            return orders
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    async def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            if order_id in self._fallback_storage["orders"]:
                self._fallback_storage["orders"][order_id]["status"] = status
                self._fallback_storage["orders"][order_id]["updated_at"] = datetime.now()
                return True
            return False
            
        try:
            result = await self.db.orders.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.now()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False
    
    # Queue Operations
    async def get_queue_items(self, kitchen_id: Optional[str] = None, status: Optional[str] = None, order_id: Optional[str] = None) -> List[Dict]:
        """Get queue items with optional filtering."""
        print("------------------------ kitchen id:", kitchen_id)
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            items = list(self._fallback_storage["queue_items"].values())
            
            # Apply filters
            if kitchen_id:
                items = [item for item in items if item.get("kitchen_id") == kitchen_id]
            if status:
                items = [item for item in items if item.get("status") == status]
            if order_id:
                items = [item for item in items if item.get("order_id") == order_id]
            
            # Sort by scheduled_start
            items.sort(key=lambda x: x.get("scheduled_start", datetime.min))
            return items

        try:
            filter_query = {}
            if kitchen_id:
                filter_query["kitchen_id"] = kitchen_id
            if status:
                filter_query["status"] = status
            if order_id:
                filter_query["order_id"] = order_id

            print(f"Getting queue items with filter: {filter_query}")

            cursor = self.db.queue_items.find(filter_query).sort("scheduled_start", 1)
            items = await cursor.to_list(length=None)

            for item in items:
                item["_id"] = str(item["_id"])

            return items

        except Exception as e:
            logger.error(f"Error getting queue items: {e}")
            return []
    
    async def upsert_queue_item(self, queue_item: Dict) -> bool:
        """Insert or update a queue item."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            queue_item["updated_at"] = datetime.now()
            self._fallback_storage["queue_items"][queue_item["queue_id"]] = queue_item
            return True
            
        try:
            queue_item["updated_at"] = datetime.now()
            
            result = await self.db.queue_items.replace_one(
                {"queue_id": queue_item["queue_id"]},
                queue_item,
                upsert=True
            )

            return True

        except Exception as e:
            logger.error(f"Error upserting queue item: {e}")
            return False

    async def update_queue_item_status(self, queue_id: str, status: str, actual_start: Optional[datetime] = None, actual_completion: Optional[datetime] = None) -> bool:
        """Update queue item status and timing."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            if queue_id in self._fallback_storage["queue_items"]:
                item = self._fallback_storage["queue_items"][queue_id]
                item["status"] = status
                item["updated_at"] = datetime.now()
                if actual_start:
                    item["actual_start"] = actual_start
                if actual_completion:
                    item["actual_completion"] = actual_completion
                return True
            return False

        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now()
            }

            if actual_start:
                update_data["actual_start"] = actual_start
            if actual_completion:
                update_data["actual_completion"] = actual_completion

            result = await self.db.queue_items.update_one(
                {"queue_id": queue_id},
                {"$set": update_data}
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error updating queue item status: {e}")
            return False

    async def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Get order by ID."""
        if not self._connected or self.db is None:
            # Fallback to in-memory storage
            return self._fallback_storage["orders"].get(order_id)

        try:
            order = await self.db.orders.find_one({"order_id": order_id})
            if order:
                order["_id"] = str(order["_id"])
            return order

        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None

    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB health."""
        if not self._connected or self.client is None:
            return {
                "status": "disconnected",
                "message": "MongoDB client not initialized or connected"
            }
            
        try:
            await self.client.admin.command('ping')
            
            # Get collection stats
            stats = {}
            collections = ["menu_items", "kitchens", "orders", "queue_items"]
            
            for collection_name in collections:
                count = await self.db[collection_name].count_documents({})
                stats[collection_name] = count
            
            return {
                "status": "connected",
                "database": self._database_name,
                "collections": stats
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Global MongoDB service instance
mongodb_service = MongoDBService()