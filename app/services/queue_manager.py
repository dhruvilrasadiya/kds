"""
Kitchen Queue Manager for the Smart Kitchen Queue Management System.
Now uses MongoDB exclusively for all data operations.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import threading

from app.models import QueueItem, ItemStatus, KitchenStatusModel, PriorityLevel
from app.services.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)


class KitchenQueueManager:
    """Manages queues for all kitchens in the system using MongoDB."""

    def __init__(self):
        """Initialize the kitchen queue manager with MongoDB backend."""
        self.mongodb_service = mongodb_service
        self._lock = threading.RLock()  # Thread-safe operations
        self._kitchen_configs_cache: Dict = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)  # Cache kitchen configs for 5 minutes
    
    async def _load_kitchen_configs(self):
        """Load kitchen configurations from MongoDB with caching."""
        try:
            # Check cache validity
            if (self._cache_timestamp and
                datetime.now() - self._cache_timestamp < self._cache_ttl and
                self._kitchen_configs_cache):
                return self._kitchen_configs_cache

            # Load from MongoDB
            kitchens = await self.mongodb_service.get_kitchens()
            self._kitchen_configs_cache = {
                kitchen['kitchen_id']: kitchen for kitchen in kitchens
            }
            self._cache_timestamp = datetime.now()

            logger.info(f"Loaded configurations for {len(self._kitchen_configs_cache)} kitchens from MongoDB")
            return self._kitchen_configs_cache

        except Exception as e:
            logger.error(f"Failed to load kitchen configurations from MongoDB: {e}")
            # Return cached data if available
            if self._kitchen_configs_cache:
                logger.warning("Using cached kitchen configurations")
                return self._kitchen_configs_cache
            raise

    async def get_kitchen_current_load(self, kitchen_id: str) -> int:
        """Get the current load (number of active items) for a kitchen from MongoDB."""
        try:
            # Get active queue items for this kitchen
            active_items = await self.mongodb_service.get_queue_items(
                kitchen_id=kitchen_id,
                status=None  # We'll filter by status below
            )

            # Count items that are queued or in progress
            active_count = sum(
                1 for item in active_items
                if item.get('status') in ['queued', 'in_progress']
            )

            return active_count

        except Exception as e:
            logger.error(f"Error getting current load for kitchen {kitchen_id}: {e}")
            return 0
    
    async def add_item_to_queue(self, kitchen_id: str, item: QueueItem) -> bool:
        """Add an item to a kitchen's queue in MongoDB."""
        try:
            # Load kitchen configs
            kitchen_configs = await self._load_kitchen_configs()

            if kitchen_id not in kitchen_configs:
                logger.error(f"Kitchen {kitchen_id} not found in configuration")
                return False

            # Check capacity
            if not await self.check_kitchen_capacity(kitchen_id):
                logger.warning(f"Kitchen {kitchen_id} is at full capacity")
                return False

            # Prepare queue item data for MongoDB
            queue_item_data = {
                "queue_id": f"Q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{item.item_id}",
                "order_id": getattr(item, 'order_id', None),
                "item_id": item.item_id,
                "kitchen_id": kitchen_id,
                "status": "queued",
                "priority_level": item.priority_level.value if hasattr(item.priority_level, 'value') else str(item.priority_level),
                "scheduled_start": item.scheduled_start,
                "estimated_completion": item.estimated_completion,
                "prep_time_minutes": item.prep_time,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # Save to MongoDB
            success = await self.mongodb_service.upsert_queue_item(queue_item_data)

            if success:
                logger.info(f"Added item {item.item_id} to kitchen {kitchen_id} queue in MongoDB")
                return True
            else:
                logger.error(f"Failed to add item {item.item_id} to MongoDB")
                return False

        except Exception as e:
            logger.error(f"Error adding item to queue: {e}")
            return False
    
    async def update_item_status(self, kitchen_id: str, item_id: str, status: str) -> bool:
        """Update item status in MongoDB."""
        try:
            # Get the queue item first
            queue_items = await self.mongodb_service.get_queue_items(kitchen_id=kitchen_id)
            target_item = None

            for item in queue_items:
                if item.get('item_id') == item_id:
                    target_item = item
                    break

            if not target_item:
                logger.warning(f"Item {item_id} not found in kitchen {kitchen_id} queue")
                return False

            # Update status in MongoDB
            additional_data = {}
            if status == "in_progress":
                additional_data["actual_start"] = datetime.now()
            elif status == "completed":
                additional_data["actual_completion"] = datetime.now()

            success = await self.mongodb_service.update_queue_item_status(
                target_item["queue_id"],
                status,
                **additional_data
            )

            if success:
                logger.info(f"Updated item {item_id} status to {status} in kitchen {kitchen_id}")
                
                # If item is completed, check if all items in the order are completed
                if status == "completed" and target_item.get("order_id"):
                    order_id = target_item.get("order_id")
                    # Get all queue items for this order
                    order_items = await self.mongodb_service.get_queue_items(order_id=order_id)
                    
                    # Check if all items are completed
                    all_completed = all(item.get('status') == 'completed' for item in order_items)
                    
                    if all_completed:
                        # Update order status to completed in MongoDB
                        await self.mongodb_service.update_order_status(order_id, "completed")
                        logger.info(f"All items completed for order {order_id}, marked as completed")
                
                return True
            else:
                logger.error(f"Failed to update item {item_id} status in MongoDB")
                return False

        except Exception as e:
            logger.error(f"Error updating item status: {e}")
            return False
    
    async def remove_completed_item(self, kitchen_id: str, item_id: str) -> bool:
        """Mark an item as completed in MongoDB."""
        # This method calls update_item_status which now handles order status updates
        return await self.update_item_status(kitchen_id, item_id, "completed")
    
    async def get_estimated_completion_time(self, kitchen_id: str) -> datetime:
        """Get estimated completion time for all items in a kitchen's queue from MongoDB."""
        try:
            current_time = datetime.now()
            estimated_time = current_time

            # Get active items from MongoDB
            queue_items = await self.mongodb_service.get_queue_items(kitchen_id=kitchen_id)
            active_items = [
                item for item in queue_items
                if item.get('status') in ['queued', 'in_progress']
            ]

            # Sort by scheduled start time
            active_items.sort(key=lambda x: x.get('scheduled_start', current_time))

            for item in active_items:
                if item.get('status') == 'in_progress':
                    # Item is already in progress, use its estimated completion
                    item_completion = item.get('estimated_completion', current_time)
                    if isinstance(item_completion, str):
                        # Parse datetime string if needed
                        from dateutil.parser import parse
                        item_completion = parse(item_completion)
                    estimated_time = max(estimated_time, item_completion)
                else:
                    # Item is queued, add its prep time
                    scheduled_start = item.get('scheduled_start', current_time)
                    if isinstance(scheduled_start, str):
                        from dateutil.parser import parse
                        scheduled_start = parse(scheduled_start)
                    prep_time = item.get('prep_time_minutes', 10)
                    estimated_time = max(estimated_time, scheduled_start) + timedelta(minutes=prep_time)

            return estimated_time

        except Exception as e:
            logger.error(f"Error calculating estimated completion time: {e}")
            return datetime.now()
    
    async def check_kitchen_capacity(self, kitchen_id: str) -> bool:
        """Check if a kitchen has available capacity using MongoDB data."""
        try:
            kitchen_configs = await self._load_kitchen_configs()

            if kitchen_id not in kitchen_configs:
                return False

            capacity = kitchen_configs[kitchen_id].get('capacity', 1)
            current_load = await self.get_kitchen_current_load(kitchen_id)

            return current_load < capacity

        except Exception as e:
            logger.error(f"Error checking kitchen capacity: {e}")
            return False
    
    async def get_kitchen_status(self, kitchen_id: str) -> Optional[KitchenStatusModel]:
        """Get comprehensive status for a kitchen from MongoDB."""
        try:
            kitchen_configs = await self._load_kitchen_configs()

            if kitchen_id not in kitchen_configs:
                return None

            config = kitchen_configs[kitchen_id]

            # Get current queue items from MongoDB
            queue_items = await self.mongodb_service.get_queue_items(kitchen_id=kitchen_id)

            # Convert MongoDB items to QueueItem objects for compatibility
            current_queue = []
            for item_data in queue_items:
                try:
                    queue_item = QueueItem(
                        item_id=item_data.get('item_id', ''),
                        item_name=item_data.get('item_name',''),
                        order_id=item_data.get('order_id', ''),
                        kitchen_id=item_data.get('kitchen_id', ''),
                        prep_time=item_data.get('prep_time_minutes', 10),
                        scheduled_start=item_data.get('scheduled_start', datetime.now()),
                        estimated_completion=item_data.get('estimated_completion', datetime.now()),
                        status=ItemStatus(item_data.get('status', 'queued')),
                        priority_level=PriorityLevel(item_data.get('priority_level', 'normal'))
                    )
                    current_queue.append(queue_item)
                except Exception as e:
                    logger.warning(f"Error converting queue item: {e}")
                    continue

            current_load = await self.get_kitchen_current_load(kitchen_id)
            available_slots = config.get('capacity', 1) - current_load
            next_available_time = await self.get_estimated_completion_time(kitchen_id)

            return KitchenStatusModel(
                kitchen_id=kitchen_id,
                kitchen_name=config.get('kitchen_name', config.get('name', kitchen_id)),
                current_queue=current_queue,
                capacity=config.get('capacity', 1),
                current_load=current_load,
                available_slots=available_slots,
                next_available_time=next_available_time,
                status=config.get('status', 'active'),
                specialization=config.get('specialization', 'general')
            )

        except Exception as e:
            logger.error(f"Error getting kitchen status: {e}")
            return None

    async def get_all_kitchen_statuses(self) -> List[KitchenStatusModel]:
        """Get status for all kitchens from MongoDB."""
        try:
            kitchen_configs = await self._load_kitchen_configs()
            statuses = []

            for kitchen_id in kitchen_configs.keys():
                status = await self.get_kitchen_status(kitchen_id)
                if status:
                    statuses.append(status)
            return statuses

        except Exception as e:
            logger.error(f"Error getting all kitchen statuses: {e}")
            return []

    async def get_queue_items_by_order(self, order_id: str) -> List[QueueItem]:
        """Get all queue items for a specific order from MongoDB."""
        try:
            queue_items_data = await self.mongodb_service.get_queue_items(order_id=order_id)
            items = []

            for item_data in queue_items_data:
                try:
                    queue_item = QueueItem(
                        item_id=item_data.get('item_id', ''),
                        item_name=item_data.get('item_name',''),
                        order_id=item_data.get('order_id', ''),
                        kitchen_id=item_data.get('kitchen_id', ''),
                        prep_time=item_data.get('prep_time_minutes', 10),
                        scheduled_start=item_data.get('scheduled_start', datetime.now()),
                        estimated_completion=item_data.get('estimated_completion', datetime.now()),
                        status=ItemStatus(item_data.get('status', 'queued')),
                        priority_level=PriorityLevel(item_data.get('priority_level', 'normal'))
                    )
                    items.append(queue_item)
                except Exception as e:
                    logger.warning(f"Error converting queue item: {e}")
                    continue

            return items

        except Exception as e:
            logger.error(f"Error getting queue items by order: {e}")
            return []


    async def get_next_available_slot(self, kitchen_id: str) -> datetime:
        """Get the next available time slot for a kitchen."""
        try:
            if not await self.check_kitchen_capacity(kitchen_id):
                # Kitchen is at capacity, return estimated completion time
                return await self.get_estimated_completion_time(kitchen_id)
            else:
                # Kitchen has capacity, can start immediately
                return datetime.now()
        except Exception as e:
            logger.error(f"Error getting next available slot for kitchen {kitchen_id}: {e}")
            return datetime.now()

    async def reorder_queue_by_priority(self, kitchen_id: str):
        """Reorder a kitchen's queue based on current priorities using MongoDB."""
        try:
            # Get current queue items from MongoDB
            queue_items = await self.mongodb_service.get_queue_items(kitchen_id=kitchen_id)

            if not queue_items:
                logger.info(f"No queue items found for kitchen {kitchen_id}")
                return

            # Separate completed items from active ones
            completed_items = [item for item in queue_items if item.get('status') == 'completed']
            active_items = [item for item in queue_items if item.get('status') != 'completed']

            # Sort active items by priority and scheduled time
            priority_order = {
                'emergency': 0,
                'high': 1,
                'normal': 2,
                'low': 3
            }

            def sort_key(item):
                priority = item.get('priority_level', 'normal')
                priority_value = priority_order.get(priority, 2)
                scheduled_start = item.get('scheduled_start', datetime.now())
                if isinstance(scheduled_start, str):
                    from dateutil.parser import parse
                    scheduled_start = parse(scheduled_start)
                return (priority_value, scheduled_start)

            active_items.sort(key=sort_key)

            logger.info(f"Reordered queue for kitchen {kitchen_id} with {len(active_items)} active items")

        except Exception as e:
            logger.error(f"Error reordering queue for kitchen {kitchen_id}: {e}")

    def clear_completed_items(self, kitchen_id: str, older_than_hours: int = 24):
        """Clear completed items older than specified hours."""
        with self._lock:
            if kitchen_id not in self._kitchen_queues:
                return

            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            original_count = len(self._kitchen_queues[kitchen_id])

            self._kitchen_queues[kitchen_id] = [
                item for item in self._kitchen_queues[kitchen_id]
                if not (item.status == ItemStatus.COMPLETED and
                       item.actual_completion and
                       item.actual_completion < cutoff_time)
            ]

            cleared_count = original_count - len(self._kitchen_queues[kitchen_id])
            if cleared_count > 0:
                logger.info(f"Cleared {cleared_count} completed items from kitchen {kitchen_id}")

    def get_kitchen_efficiency_metrics(self, kitchen_id: str) -> Dict:
        """Get efficiency metrics for a kitchen."""
        with self._lock:
            if kitchen_id not in self._kitchen_queues:
                return {}

            completed_items = [
                item for item in self._kitchen_queues[kitchen_id]
                if item.status == ItemStatus.COMPLETED and item.actual_completion
            ]

            if not completed_items:
                return {"total_completed": 0}

            total_items = len(completed_items)
            total_scheduled_time = sum(item.prep_time for item in completed_items)
            total_actual_time = sum(
                (item.actual_completion - item.actual_start).total_seconds() / 60
                for item in completed_items
                if item.actual_start and item.actual_completion
            )

            avg_delay = sum(
                max(0, (item.actual_completion - item.estimated_completion).total_seconds() / 60)
                for item in completed_items
                if item.actual_completion and item.estimated_completion
            ) / total_items if total_items > 0 else 0

            return {
                "total_completed": total_items,
                "avg_scheduled_time": total_scheduled_time / total_items if total_items > 0 else 0,
                "avg_actual_time": total_actual_time / total_items if total_items > 0 else 0,
                "avg_delay_minutes": avg_delay,
                "efficiency_ratio": (total_scheduled_time / total_actual_time) if total_actual_time > 0 else 0
            }
