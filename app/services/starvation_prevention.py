"""
Anti-Starvation Prevention System for the Smart Kitchen Queue Management System.
"""

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import threading

from app.models import QueueItem, PriorityLevel
from app.config import config

logger = logging.getLogger(__name__)


class StarvationPrevention:
    """Manages anti-starvation mechanisms to prevent items from being perpetually delayed."""
    
    def __init__(self, max_delays: Optional[int] = None):
        """Initialize the starvation prevention system."""
        self.max_delays = max_delays or config.MAX_STARVATION_COUNT
        self.item_delay_counter: Dict[str, int] = defaultdict(int)
        self.item_first_delay_time: Dict[str, datetime] = {}
        self.emergency_items: Set[str] = set()
        self.starvation_history: List[Dict] = []
        self._lock = threading.RLock()
        
        logger.info(f"Starvation prevention initialized with max_delays={self.max_delays}")
    
    def check_starvation(self, item_id: str) -> bool:
        """Check if an item is experiencing starvation (delayed too many times)."""
        with self._lock:
            delay_count = self.item_delay_counter.get(item_id, 0)
            is_starving = delay_count >= self.max_delays
            
            if is_starving and item_id not in self.emergency_items:
                logger.warning(f"Item {item_id} is starving with {delay_count} delays")
                self.emergency_items.add(item_id)
                self._record_starvation_event(item_id, delay_count)
            
            return is_starving
    
    def increment_delay_counter(self, item_id: str, reason: str = "scheduling_conflict"):
        """Increment the delay counter for an item."""
        with self._lock:
            self.item_delay_counter[item_id] += 1
            current_count = self.item_delay_counter[item_id]
            
            # Record first delay time
            if current_count == 1:
                self.item_first_delay_time[item_id] = datetime.now()
            
            logger.info(f"Item {item_id} delayed (count: {current_count}, reason: {reason})")
            
            # Check if item is now starving
            if current_count >= self.max_delays:
                self.check_starvation(item_id)
    
    def apply_emergency_priority(self, item_id: str) -> Dict:
        """Apply emergency priority to a starving item."""
        with self._lock:
            if item_id not in self.emergency_items:
                logger.warning(f"Attempting to apply emergency priority to non-starving item {item_id}")
                return {"applied": False, "reason": "item_not_starving"}
            
            emergency_config = {
                "priority": PriorityLevel.EMERGENCY,
                "force_schedule": True,
                "bypass_optimization": True,
                "immediate_processing": True,
                "starvation_boost": True
            }
            
            logger.critical(f"Applied emergency priority to starving item {item_id}")
            
            # Record emergency intervention
            self._record_emergency_intervention(item_id)
            
            return {
                "applied": True,
                "config": emergency_config,
                "delay_count": self.item_delay_counter[item_id],
                "first_delay_time": self.item_first_delay_time.get(item_id)
            }
    
    def reset_item_counters(self, item_id: str):
        """Reset counters for an item (called when item is successfully processed)."""
        with self._lock:
            if item_id in self.item_delay_counter:
                delay_count = self.item_delay_counter[item_id]
                del self.item_delay_counter[item_id]
                
                if item_id in self.item_first_delay_time:
                    del self.item_first_delay_time[item_id]
                
                if item_id in self.emergency_items:
                    self.emergency_items.remove(item_id)
                    logger.info(f"Removed item {item_id} from emergency list after successful processing")
                
                if delay_count > 0:
                    logger.info(f"Reset delay counters for item {item_id} (was delayed {delay_count} times)")
    
    def get_starving_items(self) -> List[str]:
        """Get list of currently starving items."""
        with self._lock:
            return list(self.emergency_items)
    
    def get_item_delay_info(self, item_id: str) -> Dict:
        """Get delay information for a specific item."""
        with self._lock:
            delay_count = self.item_delay_counter.get(item_id, 0)
            first_delay = self.item_first_delay_time.get(item_id)
            is_emergency = item_id in self.emergency_items
            
            info = {
                "item_id": item_id,
                "delay_count": delay_count,
                "is_starving": delay_count >= self.max_delays,
                "is_emergency": is_emergency,
                "first_delay_time": first_delay,
                "time_since_first_delay": None
            }
            
            if first_delay:
                info["time_since_first_delay"] = (datetime.now() - first_delay).total_seconds() / 60
            
            return info
    
    def get_starvation_statistics(self) -> Dict:
        """Get overall starvation statistics."""
        with self._lock:
            total_delayed_items = len(self.item_delay_counter)
            currently_starving = len(self.emergency_items)
            total_starvation_events = len(self.starvation_history)
            
            # Calculate average delay count
            avg_delay_count = (
                sum(self.item_delay_counter.values()) / total_delayed_items
                if total_delayed_items > 0 else 0
            )
            
            # Get delay distribution
            delay_distribution = defaultdict(int)
            for count in self.item_delay_counter.values():
                delay_distribution[count] += 1
            
            return {
                "total_delayed_items": total_delayed_items,
                "currently_starving": currently_starving,
                "total_starvation_events": total_starvation_events,
                "average_delay_count": avg_delay_count,
                "delay_distribution": dict(delay_distribution),
                "max_delays_threshold": self.max_delays,
                "emergency_items": list(self.emergency_items)
            }
    
    def _record_starvation_event(self, item_id: str, delay_count: int):
        """Record a starvation event for analytics."""
        event = {
            "timestamp": datetime.now(),
            "item_id": item_id,
            "delay_count": delay_count,
            "first_delay_time": self.item_first_delay_time.get(item_id),
            "event_type": "starvation_detected"
        }
        
        self.starvation_history.append(event)
        
        # Keep only recent history (last 1000 events)
        if len(self.starvation_history) > 1000:
            self.starvation_history = self.starvation_history[-1000:]
    
    def _record_emergency_intervention(self, item_id: str):
        """Record an emergency intervention for analytics."""
        event = {
            "timestamp": datetime.now(),
            "item_id": item_id,
            "delay_count": self.item_delay_counter.get(item_id, 0),
            "first_delay_time": self.item_first_delay_time.get(item_id),
            "event_type": "emergency_intervention"
        }
        
        self.starvation_history.append(event)
    
    def apply_starvation_boost_to_queue_item(self, queue_item: QueueItem) -> QueueItem:
        """Apply starvation boost to a queue item if it's starving."""
        with self._lock:
            if self.check_starvation(queue_item.item_id):
                # Apply emergency priority
                queue_item.priority_level = PriorityLevel.EMERGENCY
                queue_item.starvation_count = self.item_delay_counter[queue_item.item_id]
                
                # Move scheduled start time to immediate
                queue_item.scheduled_start = datetime.now()
                
                logger.critical(f"Applied starvation boost to queue item {queue_item.item_id}")
            
            return queue_item
    
    def should_bypass_optimization(self, item_id: str) -> bool:
        """Check if an item should bypass normal optimization due to starvation."""
        with self._lock:
            return item_id in self.emergency_items
    
    def get_priority_boost_factor(self, item_id: str) -> float:
        """Get priority boost factor based on delay count."""
        with self._lock:
            delay_count = self.item_delay_counter.get(item_id, 0)
            
            if delay_count == 0:
                return 1.0
            elif delay_count < self.max_delays:
                # Gradual boost before starvation
                return 1.0 + (delay_count * 0.2)
            else:
                # Maximum boost for starving items
                return 3.0
    
    def cleanup_old_entries(self, max_age_hours: int = 24):
        """Clean up old delay entries for items that haven't been seen recently."""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            items_to_remove = []
            
            for item_id, first_delay_time in self.item_first_delay_time.items():
                if first_delay_time < cutoff_time:
                    items_to_remove.append(item_id)
            
            for item_id in items_to_remove:
                if item_id in self.item_delay_counter:
                    del self.item_delay_counter[item_id]
                if item_id in self.item_first_delay_time:
                    del self.item_first_delay_time[item_id]
                if item_id in self.emergency_items:
                    self.emergency_items.remove(item_id)
            
            if items_to_remove:
                logger.info(f"Cleaned up {len(items_to_remove)} old starvation entries")
