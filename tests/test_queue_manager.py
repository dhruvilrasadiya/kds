"""
Unit tests for KitchenQueueManager.
"""

import pytest
from datetime import datetime, timedelta

from app.services.queue_manager import KitchenQueueManager
from app.models import QueueItem, ItemStatus, PriorityLevel


class TestKitchenQueueManager:
    """Test cases for KitchenQueueManager."""
    
    def test_initialization(self, queue_manager):
        """Test queue manager initialization."""
        assert queue_manager is not None
        assert len(queue_manager._kitchen_configs) == 3
        assert "KITCHEN_A" in queue_manager._kitchen_configs
    
    def test_get_kitchen_current_load(self, queue_manager, sample_queue_item):
        """Test getting current kitchen load."""
        # Initially should be 0
        load = queue_manager.get_kitchen_current_load("KITCHEN_A")
        assert load == 0
        
        # Add an item
        queue_manager.add_item_to_queue("KITCHEN_A", sample_queue_item)
        load = queue_manager.get_kitchen_current_load("KITCHEN_A")
        assert load == 1
    
    def test_add_item_to_queue(self, queue_manager, sample_queue_item):
        """Test adding item to queue."""
        success = queue_manager.add_item_to_queue("KITCHEN_A", sample_queue_item)
        assert success is True
        
        # Check item was added
        load = queue_manager.get_kitchen_current_load("KITCHEN_A")
        assert load == 1
        
        # Test invalid kitchen
        success = queue_manager.add_item_to_queue("INVALID_KITCHEN", sample_queue_item)
        assert success is False
    
    def test_check_kitchen_capacity(self, queue_manager, test_utils):
        """Test kitchen capacity checking."""
        # Initially should have capacity
        has_capacity = queue_manager.check_kitchen_capacity("KITCHEN_A")
        assert has_capacity is True
        
        # Fill kitchen to capacity (3 items for KITCHEN_A)
        items = test_utils.create_test_queue_items(3, "KITCHEN_A")
        for item in items:
            queue_manager.add_item_to_queue("KITCHEN_A", item)
        
        # Should still have capacity (items are queued, not in progress)
        has_capacity = queue_manager.check_kitchen_capacity("KITCHEN_A")
        assert has_capacity is False  # All slots taken by queued items
    
    def test_remove_completed_item(self, queue_manager, sample_queue_item):
        """Test removing completed item."""
        # Add item first
        queue_manager.add_item_to_queue("KITCHEN_A", sample_queue_item)
        
        # Remove it
        success = queue_manager.remove_completed_item("KITCHEN_A", sample_queue_item.item_id)
        assert success is True
        
        # Try to remove non-existent item
        success = queue_manager.remove_completed_item("KITCHEN_A", "NON_EXISTENT")
        assert success is False
    
    def test_get_estimated_completion_time(self, queue_manager, test_utils):
        """Test getting estimated completion time."""
        # Add multiple items
        items = test_utils.create_test_queue_items(3, "KITCHEN_A")
        for item in items:
            queue_manager.add_item_to_queue("KITCHEN_A", item)
        
        completion_time = queue_manager.get_estimated_completion_time("KITCHEN_A")
        assert isinstance(completion_time, datetime)
        assert completion_time > datetime.now()
    
    def test_priority_insertion(self, queue_manager, test_utils):
        """Test that items are inserted based on priority."""
        # Create items with different priorities
        normal_item = test_utils.create_test_queue_items(1, "KITCHEN_A")[0]
        normal_item.priority_level = PriorityLevel.NORMAL
        
        high_item = test_utils.create_test_queue_items(1, "KITCHEN_A")[0]
        high_item.item_id = "HIGH_PRIORITY"
        high_item.priority_level = PriorityLevel.HIGH
        
        emergency_item = test_utils.create_test_queue_items(1, "KITCHEN_A")[0]
        emergency_item.item_id = "EMERGENCY"
        emergency_item.priority_level = PriorityLevel.EMERGENCY
        
        # Add in reverse priority order
        queue_manager.add_item_to_queue("KITCHEN_A", normal_item)
        queue_manager.add_item_to_queue("KITCHEN_A", high_item)
        queue_manager.add_item_to_queue("KITCHEN_A", emergency_item)
        
        # Check queue order
        status = queue_manager.get_kitchen_status("KITCHEN_A")
        queue = status.current_queue
        
        # Emergency should be first, then high, then normal
        assert queue[0].priority_level == PriorityLevel.EMERGENCY
        assert queue[1].priority_level == PriorityLevel.HIGH
        assert queue[2].priority_level == PriorityLevel.NORMAL
    
    def test_get_kitchen_status(self, queue_manager, sample_queue_item):
        """Test getting kitchen status."""
        # Add an item
        queue_manager.add_item_to_queue("KITCHEN_A", sample_queue_item)
        
        status = queue_manager.get_kitchen_status("KITCHEN_A")
        assert status is not None
        assert status.kitchen_id == "KITCHEN_A"
        assert status.kitchen_name == "Grill Station"
        assert status.capacity == 3
        assert status.current_load == 1
        assert status.available_slots == 2
        assert len(status.current_queue) == 1
    
    def test_get_all_kitchen_statuses(self, queue_manager):
        """Test getting all kitchen statuses."""
        statuses = queue_manager.get_all_kitchen_statuses()
        assert len(statuses) == 3
        
        kitchen_ids = [status.kitchen_id for status in statuses]
        assert "KITCHEN_A" in kitchen_ids
        assert "KITCHEN_B" in kitchen_ids
        assert "KITCHEN_C" in kitchen_ids
    
    def test_update_item_status(self, queue_manager, sample_queue_item):
        """Test updating item status."""
        # Add item
        queue_manager.add_item_to_queue("KITCHEN_A", sample_queue_item)
        
        # Update status
        success = queue_manager.update_item_status(
            "KITCHEN_A", sample_queue_item.item_id, ItemStatus.IN_PROGRESS, datetime.now()
        )
        assert success is True
        
        # Check status was updated
        status = queue_manager.get_kitchen_status("KITCHEN_A")
        item = status.current_queue[0]
        assert item.status == ItemStatus.IN_PROGRESS
        assert item.actual_start is not None
    
    def test_get_queue_items_by_order(self, queue_manager, test_utils):
        """Test getting queue items by order."""
        # Create items for same order
        items = test_utils.create_test_queue_items(2, "KITCHEN_A")
        items[0].order_id = "TEST_ORDER"
        items[1].order_id = "TEST_ORDER"
        
        # Add to different kitchens
        queue_manager.add_item_to_queue("KITCHEN_A", items[0])
        queue_manager.add_item_to_queue("KITCHEN_B", items[1])
        
        # Get items by order
        order_items = queue_manager.get_queue_items_by_order("TEST_ORDER")
        assert len(order_items) == 2
        
        order_ids = [item.order_id for item in order_items]
        assert all(order_id == "TEST_ORDER" for order_id in order_ids)
    
    def test_reorder_queue_by_priority(self, queue_manager, test_utils):
        """Test reordering queue by priority."""
        # Create items with different priorities
        items = test_utils.create_test_queue_items(3, "KITCHEN_A")
        items[0].priority_level = PriorityLevel.LOW
        items[1].priority_level = PriorityLevel.HIGH
        items[2].priority_level = PriorityLevel.NORMAL
        
        # Add items
        for item in items:
            queue_manager.add_item_to_queue("KITCHEN_A", item)
        
        # Reorder
        queue_manager.reorder_queue_by_priority("KITCHEN_A")
        
        # Check order
        status = queue_manager.get_kitchen_status("KITCHEN_A")
        queue = status.current_queue
        
        # Should be HIGH, NORMAL, LOW
        assert queue[0].priority_level == PriorityLevel.HIGH
        assert queue[1].priority_level == PriorityLevel.NORMAL
        assert queue[2].priority_level == PriorityLevel.LOW
    
    def test_clear_completed_items(self, queue_manager, sample_queue_item):
        """Test clearing completed items."""
        # Add and complete an item
        queue_manager.add_item_to_queue("KITCHEN_A", sample_queue_item)
        queue_manager.remove_completed_item("KITCHEN_A", sample_queue_item.item_id)
        
        # Clear completed items
        queue_manager.clear_completed_items("KITCHEN_A", 0)  # Clear immediately
        
        # Queue should be empty or only have active items
        status = queue_manager.get_kitchen_status("KITCHEN_A")
        active_items = [item for item in status.current_queue if item.status != ItemStatus.COMPLETED]
        assert len(active_items) == 0
    
    def test_get_kitchen_efficiency_metrics(self, queue_manager, sample_queue_item):
        """Test getting kitchen efficiency metrics."""
        # Add and complete an item
        queue_manager.add_item_to_queue("KITCHEN_A", sample_queue_item)
        sample_queue_item.actual_start = datetime.now()
        sample_queue_item.actual_completion = datetime.now() + timedelta(minutes=16)
        queue_manager.remove_completed_item("KITCHEN_A", sample_queue_item.item_id)
        
        metrics = queue_manager.get_kitchen_efficiency_metrics("KITCHEN_A")
        assert isinstance(metrics, dict)
        assert "total_completed" in metrics
