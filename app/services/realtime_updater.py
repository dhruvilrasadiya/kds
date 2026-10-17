"""
Real-time Update Mechanism for the Smart Kitchen Queue Management System.
"""

import asyncio
import logging
import threading
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.services.ai_agent import KitchenAIAgent
from app.services.performance_learning import PerformanceLearning
from app.models import ItemStatus, QueueItem

logger = logging.getLogger(__name__)


class RealTimeUpdater:
    """Manages real-time updates and triggers rescheduling when needed."""
    
    def __init__(self, queue_manager: KitchenQueueManager, 
                 starvation_prevention: StarvationPrevention,
                 ai_agent: KitchenAIAgent,
                 performance_learning: PerformanceLearning):
        """Initialize the real-time updater."""
        self.queue_manager = queue_manager
        self.starvation_prevention = starvation_prevention
        self.ai_agent = ai_agent
        self.performance_learning = performance_learning
        
        # Event callbacks
        self.update_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        self.starvation_callbacks: List[Callable] = []
        
        # Update tracking
        self.last_update_time = datetime.now()
        self.update_history: List[Dict] = []
        self.pending_updates: Dict[str, Dict] = {}
        
        # Threading for background tasks
        self._lock = threading.RLock()
        self._background_thread = None
        self._stop_background = False
        
        # Start background monitoring
        self.start_background_monitoring()
        
        logger.info("Real-time updater initialized")
    
    def start_background_monitoring(self):
        """Start background thread for continuous monitoring."""
        if self._background_thread is None or not self._background_thread.is_alive():
            self._stop_background = False
            self._background_thread = threading.Thread(
                target=self._background_monitor,
                daemon=True
            )
            self._background_thread.start()
            logger.info("Background monitoring started")
    
    def stop_background_monitoring(self):
        """Stop background monitoring thread."""
        self._stop_background = True
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join(timeout=5)
        logger.info("Background monitoring stopped")
    
    def _background_monitor(self):
        """Background monitoring loop."""
        while not self._stop_background:
            try:
                # Check for starvation every 30 seconds
                self._check_starvation_status()
                
                # Process pending updates
                self._process_pending_updates()
                
                # Clean up old update history
                self._cleanup_update_history()
                
                # Sleep for 30 seconds
                for _ in range(30):
                    if self._stop_background:
                        break
                    threading.Event().wait(1)
                    
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                threading.Event().wait(10)  # Wait 10 seconds before retrying
    
    def item_completed(self, kitchen_id: str, item_id: str, order_id: str,
                      actual_completion_time: Optional[datetime] = None):
        """Handle item completion and trigger necessary updates."""
        try:
            with self._lock:
                completion_time = actual_completion_time or datetime.now()
                
                # Record the completion event
                completion_event = {
                    "event_type": "item_completed",
                    "kitchen_id": kitchen_id,
                    "item_id": item_id,
                    "order_id": order_id,
                    "completion_time": completion_time,
                    "timestamp": datetime.now()
                }
                
                self.update_history.append(completion_event)
                
                # Update kitchen queue
                success = self.queue_manager.remove_completed_item(kitchen_id, item_id)
                if not success:
                    logger.warning(f"Failed to remove completed item {item_id} from kitchen {kitchen_id}")
                    return
                
                # Reset starvation counters
                self.starvation_prevention.reset_item_counters(item_id)
                
                # Check if this completion affects other items
                self._analyze_completion_impact(kitchen_id, item_id, order_id)
                
                # Trigger callbacks
                for callback in self.completion_callbacks:
                    try:
                        callback(completion_event)
                    except Exception as e:
                        logger.error(f"Error in completion callback: {e}")
                
                # Check if rescheduling is needed
                if self._should_trigger_reschedule(kitchen_id):
                    self.trigger_reschedule(reason=f"item_completion_{item_id}")
                
                logger.info(f"Item {item_id} completion processed successfully")
                
        except Exception as e:
            logger.error(f"Error processing item completion: {e}")
    
    def item_started(self, kitchen_id: str, item_id: str, order_id: str,
                    actual_start_time: Optional[datetime] = None):
        """Handle item start and update status."""
        try:
            with self._lock:
                start_time = actual_start_time or datetime.now()
                
                # Update item status
                success = self.queue_manager.update_item_status(
                    kitchen_id, item_id, ItemStatus.IN_PROGRESS, start_time
                )
                
                if success:
                    start_event = {
                        "event_type": "item_started",
                        "kitchen_id": kitchen_id,
                        "item_id": item_id,
                        "order_id": order_id,
                        "start_time": start_time,
                        "timestamp": datetime.now()
                    }
                    
                    self.update_history.append(start_event)
                    
                    # Trigger update callbacks
                    for callback in self.update_callbacks:
                        try:
                            callback(start_event)
                        except Exception as e:
                            logger.error(f"Error in update callback: {e}")
                    
                    logger.info(f"Item {item_id} started in kitchen {kitchen_id}")
                else:
                    logger.warning(f"Failed to start item {item_id} in kitchen {kitchen_id}")
                    
        except Exception as e:
            logger.error(f"Error processing item start: {e}")
    
    def trigger_reschedule(self, reason: str = "manual_trigger"):
        """Trigger AI-driven rescheduling of pending items."""
        try:
            with self._lock:
                reschedule_event = {
                    "event_type": "reschedule_triggered",
                    "reason": reason,
                    "timestamp": datetime.now()
                }
                
                self.update_history.append(reschedule_event)
                
                # Get pending orders and reoptimize
                reoptimization_results = self.ai_agent.reoptimize_pending_orders()
                
                # Apply new schedules to queues
                for result in reoptimization_results:
                    self._apply_optimization_result(result)
                
                reschedule_event["results_count"] = len(reoptimization_results)
                
                # Trigger callbacks
                for callback in self.update_callbacks:
                    try:
                        callback(reschedule_event)
                    except Exception as e:
                        logger.error(f"Error in reschedule callback: {e}")
                
                logger.info(f"Rescheduling triggered: {reason}, {len(reoptimization_results)} orders affected")
                
        except Exception as e:
            logger.error(f"Error triggering reschedule: {e}")
    
    def _check_starvation_status(self):
        """Check for starving items and trigger emergency actions."""
        try:
            starving_items = self.starvation_prevention.get_starving_items()
            
            if starving_items:
                starvation_event = {
                    "event_type": "starvation_detected",
                    "starving_items": starving_items,
                    "timestamp": datetime.now()
                }
                
                self.update_history.append(starvation_event)
                
                # Trigger emergency rescheduling
                emergency_result = self.ai_agent.emergency_reschedule(starving_items)
                starvation_event["emergency_result"] = emergency_result
                
                # Trigger starvation callbacks
                for callback in self.starvation_callbacks:
                    try:
                        callback(starvation_event)
                    except Exception as e:
                        logger.error(f"Error in starvation callback: {e}")
                
                logger.warning(f"Starvation detected for {len(starving_items)} items")
                
        except Exception as e:
            logger.error(f"Error checking starvation status: {e}")
    
    def _analyze_completion_impact(self, kitchen_id: str, completed_item_id: str, order_id: str):
        """Analyze the impact of item completion on other items."""
        try:
            # Check if this was a blocking item for other items in the same order
            order_items = self.queue_manager.get_queue_items_by_order(order_id)
            
            remaining_items = [
                item for item in order_items 
                if item.status != ItemStatus.COMPLETED and item.item_id != completed_item_id
            ]
            
            if remaining_items:
                # Check if any items can now be started earlier
                kitchen_status = self.queue_manager.get_kitchen_status(kitchen_id)
                if kitchen_status and kitchen_status.available_slots > 0:
                    # Add to pending updates for processing
                    self.pending_updates[f"order_impact_{order_id}"] = {
                        "type": "order_impact_analysis",
                        "order_id": order_id,
                        "completed_item": completed_item_id,
                        "remaining_items": [item.item_id for item in remaining_items],
                        "timestamp": datetime.now()
                    }
            
        except Exception as e:
            logger.error(f"Error analyzing completion impact: {e}")
    
    def _should_trigger_reschedule(self, kitchen_id: str) -> bool:
        """Determine if rescheduling should be triggered based on kitchen state."""
        try:
            kitchen_status = self.queue_manager.get_kitchen_status(kitchen_id)
            if not kitchen_status:
                return False
            
            # Trigger reschedule if:
            # 1. Kitchen has available capacity and queued items
            queued_items = [item for item in kitchen_status.current_queue if item.status == ItemStatus.QUEUED]
            if kitchen_status.available_slots > 0 and queued_items:
                return True
            
            # 2. There are high-priority items waiting
            high_priority_items = [
                item for item in queued_items 
                if item.priority_level.value in ["high", "emergency"]
            ]
            if high_priority_items:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking reschedule trigger: {e}")
            return False
    
    def _apply_optimization_result(self, optimization_result):
        """Apply optimization result to kitchen queues."""
        try:
            # Remove old items from queues and add optimized ones
            for item in optimization_result.optimized_items:
                # Update existing item or add new one
                success = self.queue_manager.add_item_to_queue(item.kitchen_id, item)
                if not success:
                    logger.warning(f"Failed to apply optimization for item {item.item_id}")
            
        except Exception as e:
            logger.error(f"Error applying optimization result: {e}")
    
    def _process_pending_updates(self):
        """Process pending updates that require background processing."""
        try:
            with self._lock:
                if not self.pending_updates:
                    return
                
                updates_to_process = list(self.pending_updates.items())
                self.pending_updates.clear()
                
                for update_id, update_data in updates_to_process:
                    try:
                        if update_data["type"] == "order_impact_analysis":
                            # Process order impact analysis
                            self._process_order_impact_analysis(update_data)
                        
                    except Exception as e:
                        logger.error(f"Error processing pending update {update_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing pending updates: {e}")
    
    def _process_order_impact_analysis(self, update_data: Dict):
        """Process order impact analysis."""
        try:
            order_id = update_data["order_id"]
            
            # Check if order can be completed faster now
            order_items = self.queue_manager.get_queue_items_by_order(order_id)
            
            if order_items:
                # Trigger reoptimization for this specific order
                optimization_result = self.ai_agent.optimize_order_schedule(
                    [item.item_id for item in order_items if item.status != ItemStatus.COMPLETED],
                    order_id
                )
                
                self._apply_optimization_result(optimization_result)
                
        except Exception as e:
            logger.error(f"Error processing order impact analysis: {e}")
    
    def _cleanup_update_history(self):
        """Clean up old update history entries."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            original_count = len(self.update_history)
            self.update_history = [
                event for event in self.update_history
                if event["timestamp"] > cutoff_time
            ]
            
            cleaned_count = original_count - len(self.update_history)
            if cleaned_count > 0:
                logger.debug(f"Cleaned up {cleaned_count} old update history entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up update history: {e}")
    
    def add_update_callback(self, callback: Callable):
        """Add a callback for general updates."""
        self.update_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable):
        """Add a callback for item completions."""
        self.completion_callbacks.append(callback)
    
    def add_starvation_callback(self, callback: Callable):
        """Add a callback for starvation events."""
        self.starvation_callbacks.append(callback)
    
    def get_update_history(self, hours: int = 1) -> List[Dict]:
        """Get recent update history."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self.update_history
            if event["timestamp"] > cutoff_time
        ]
    
    def get_system_status(self) -> Dict:
        """Get current real-time system status."""
        try:
            with self._lock:
                return {
                    "last_update_time": self.last_update_time.isoformat(),
                    "background_monitoring_active": self._background_thread.is_alive() if self._background_thread else False,
                    "pending_updates_count": len(self.pending_updates),
                    "update_history_count": len(self.update_history),
                    "registered_callbacks": {
                        "update_callbacks": len(self.update_callbacks),
                        "completion_callbacks": len(self.completion_callbacks),
                        "starvation_callbacks": len(self.starvation_callbacks)
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
