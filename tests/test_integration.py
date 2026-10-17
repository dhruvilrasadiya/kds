"""
Integration tests for the Smart Kitchen Queue Management System.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.services.excel_service import ExcelDataService
from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.services.performance_learning import PerformanceLearning
from app.services.realtime_updater import RealTimeUpdater
from app.models import QueueItem, PriorityLevel, ItemStatus, OrderStatus


class TestSystemIntegration:
    """Integration tests for the complete system."""
    
    def test_complete_order_workflow(self, excel_service, queue_manager, 
                                   starvation_prevention, performance_learning):
        """Test complete order processing workflow."""
        # Create order items
        order_items = ["ITM_001", "ITM_004", "ITM_007"]  # Items from different kitchens
        order_id = "INTEGRATION_TEST_ORDER"
        
        # Validate items
        assert excel_service.validate_order_items(order_items) is True
        
        # Create queue items for each order item
        menu_items = excel_service.load_menu_items()
        queue_items = []
        
        for item_id in order_items:
            item = menu_items[item_id]
            queue_item = QueueItem(
                item_id=item_id,
                item_name=item['item_name'],
                order_id=order_id,
                prep_time=item['prep_time_minutes'],
                scheduled_start=datetime.now(),
                estimated_completion=datetime.now() + timedelta(minutes=item['prep_time_minutes']),
                priority_level=PriorityLevel.NORMAL,
                starvation_count=0,
                status=ItemStatus.QUEUED,
                kitchen_id=item['kitchen_id']
            )
            queue_items.append(queue_item)
        
        # Add items to queues
        for queue_item in queue_items:
            success = queue_manager.add_item_to_queue(queue_item.kitchen_id, queue_item)
            assert success is True
        
        # Verify items are in queues
        for queue_item in queue_items:
            kitchen_status = queue_manager.get_kitchen_status(queue_item.kitchen_id)
            assert any(item.item_id == queue_item.item_id for item in kitchen_status.current_queue)
        
        # Start processing items
        for queue_item in queue_items:
            success = queue_manager.update_item_status(
                queue_item.kitchen_id, queue_item.item_id, ItemStatus.IN_PROGRESS, datetime.now()
            )
            assert success is True
        
        # Complete items and record performance
        for queue_item in queue_items:
            # Simulate completion
            actual_prep_time = queue_item.prep_time + 1  # Slight delay
            
            success = queue_manager.remove_completed_item(queue_item.kitchen_id, queue_item.item_id)
            assert success is True
            
            # Record performance
            performance_learning.record_completion(
                item_id=queue_item.item_id,
                kitchen_id=queue_item.kitchen_id,
                order_id=order_id,
                actual_time=actual_prep_time,
                scheduled_time=queue_item.prep_time,
                priority_level=queue_item.priority_level,
                kitchen_load=1,
                starvation_count=0
            )
        
        # Verify order completion
        order_queue_items = queue_manager.get_queue_items_by_order(order_id)
        completed_items = [item for item in order_queue_items if item.status == ItemStatus.COMPLETED]
        assert len(completed_items) == len(order_items)
    
    def test_starvation_prevention_integration(self, queue_manager, starvation_prevention):
        """Test starvation prevention integration with queue management."""
        item_id = "STARVING_ITEM"
        kitchen_id = "KITCHEN_A"
        
        # Create a queue item
        queue_item = QueueItem(
            item_id=item_id,
            item_name="Starving Test Item",
            order_id="STARVING_ORDER",
            prep_time=15,
            scheduled_start=datetime.now(),
            estimated_completion=datetime.now() + timedelta(minutes=15),
            priority_level=PriorityLevel.NORMAL,
            starvation_count=0,
            status=ItemStatus.QUEUED,
            kitchen_id=kitchen_id
        )
        
        # Add to queue
        queue_manager.add_item_to_queue(kitchen_id, queue_item)
        
        # Simulate delays
        for i in range(3):
            starvation_prevention.increment_delay_counter(item_id)
        
        # Item should be starving
        assert starvation_prevention.check_starvation(item_id) is True
        
        # Apply starvation boost
        boosted_item = starvation_prevention.apply_starvation_boost_to_queue_item(queue_item)
        assert boosted_item.priority_level == PriorityLevel.EMERGENCY
        
        # Update queue with boosted item
        queue_manager.add_item_to_queue(kitchen_id, boosted_item)
        
        # Reorder queue by priority
        queue_manager.reorder_queue_by_priority(kitchen_id)
        
        # Emergency item should be first
        kitchen_status = queue_manager.get_kitchen_status(kitchen_id)
        first_item = kitchen_status.current_queue[0]
        assert first_item.priority_level == PriorityLevel.EMERGENCY
    
    def test_performance_learning_integration(self, excel_service, performance_learning):
        """Test performance learning integration with historical data."""
        # Record some performance data
        performance_data = [
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'kitchen_id': 'KITCHEN_A',
                'item_id': 'ITM_001',
                'order_id': 'PERF_TEST_1',
                'actual_prep_time': 16,
                'scheduled_prep_time': 15,
                'delay_minutes': 1,
                'kitchen_load': 2
            },
            {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'kitchen_id': 'KITCHEN_A',
                'item_id': 'ITM_001',
                'order_id': 'PERF_TEST_2',
                'actual_prep_time': 17,
                'scheduled_prep_time': 15,
                'delay_minutes': 2,
                'kitchen_load': 3
            }
        ]
        
        for data in performance_data:
            excel_service.update_historical_performance(data)
        
        # Analyze kitchen efficiency
        efficiency = performance_learning.analyze_kitchen_efficiency('KITCHEN_A', 1)
        assert 'efficiency_metrics' in efficiency
        assert efficiency['total_items_analyzed'] >= 2
        
        # Update prep time estimates
        estimates = performance_learning.update_prep_time_estimates()
        assert isinstance(estimates, dict)
        
        # Identify bottlenecks
        bottlenecks = performance_learning.identify_bottlenecks()
        assert isinstance(bottlenecks, list)
    
    def test_realtime_updater_integration(self, realtime_updater, queue_manager):
        """Test real-time updater integration."""
        # Create test item
        queue_item = QueueItem(
            item_id="REALTIME_TEST",
            item_name="Real-time Test Item",
            order_id="REALTIME_ORDER",
            prep_time=15,
            scheduled_start=datetime.now(),
            estimated_completion=datetime.now() + timedelta(minutes=15),
            priority_level=PriorityLevel.NORMAL,
            starvation_count=0,
            status=ItemStatus.QUEUED,
            kitchen_id="KITCHEN_A"
        )
        
        # Add to queue
        queue_manager.add_item_to_queue("KITCHEN_A", queue_item)
        
        # Test item start
        realtime_updater.item_started("KITCHEN_A", "REALTIME_TEST", "REALTIME_ORDER")
        
        # Verify status updated
        kitchen_status = queue_manager.get_kitchen_status("KITCHEN_A")
        item = next(item for item in kitchen_status.current_queue if item.item_id == "REALTIME_TEST")
        assert item.status == ItemStatus.IN_PROGRESS
        
        # Test item completion
        realtime_updater.item_completed("KITCHEN_A", "REALTIME_TEST", "REALTIME_ORDER")
        
        # Verify completion
        kitchen_status = queue_manager.get_kitchen_status("KITCHEN_A")
        item = next(item for item in kitchen_status.current_queue if item.item_id == "REALTIME_TEST")
        assert item.status == ItemStatus.COMPLETED
    
    def test_multi_kitchen_coordination(self, excel_service, queue_manager, starvation_prevention):
        """Test coordination across multiple kitchens."""
        # Create order with items from all kitchens
        order_items = ["ITM_001", "ITM_004", "ITM_007"]  # A, B, C kitchens
        order_id = "MULTI_KITCHEN_ORDER"
        
        menu_items = excel_service.load_menu_items()
        queue_items = []
        
        # Create queue items
        for item_id in order_items:
            item = menu_items[item_id]
            queue_item = QueueItem(
                item_id=item_id,
                item_name=item['item_name'],
                order_id=order_id,
                prep_time=item['prep_time_minutes'],
                scheduled_start=datetime.now(),
                estimated_completion=datetime.now() + timedelta(minutes=item['prep_time_minutes']),
                priority_level=PriorityLevel.NORMAL,
                starvation_count=0,
                status=ItemStatus.QUEUED,
                kitchen_id=item['kitchen_id']
            )
            queue_items.append(queue_item)
        
        # Add to respective kitchen queues
        for queue_item in queue_items:
            success = queue_manager.add_item_to_queue(queue_item.kitchen_id, queue_item)
            assert success is True
        
        # Verify items are distributed across kitchens
        all_statuses = queue_manager.get_all_kitchen_statuses()
        kitchens_with_items = [
            status for status in all_statuses 
            if any(item.order_id == order_id for item in status.current_queue)
        ]
        assert len(kitchens_with_items) == 3  # All three kitchens should have items
        
        # Test synchronization - get order items
        order_queue_items = queue_manager.get_queue_items_by_order(order_id)
        assert len(order_queue_items) == 3
        
        # All items should belong to the same order
        assert all(item.order_id == order_id for item in order_queue_items)
    
    def test_capacity_management(self, queue_manager, test_utils):
        """Test kitchen capacity management."""
        kitchen_id = "KITCHEN_A"
        capacity = 3  # KITCHEN_A has capacity of 3
        
        # Fill kitchen to capacity
        items = test_utils.create_test_queue_items(capacity, kitchen_id)
        for item in items:
            success = queue_manager.add_item_to_queue(kitchen_id, item)
            assert success is True
        
        # Kitchen should be at capacity
        assert queue_manager.check_kitchen_capacity(kitchen_id) is False
        
        # Try to add one more item - should fail
        extra_item = test_utils.create_test_queue_items(1, kitchen_id)[0]
        extra_item.item_id = "EXTRA_ITEM"
        success = queue_manager.add_item_to_queue(kitchen_id, extra_item)
        assert success is False
        
        # Complete one item to free capacity
        queue_manager.remove_completed_item(kitchen_id, items[0].item_id)
        
        # Should have capacity now
        assert queue_manager.check_kitchen_capacity(kitchen_id) is True
        
        # Should be able to add the extra item now
        success = queue_manager.add_item_to_queue(kitchen_id, extra_item)
        assert success is True
    
    def test_error_handling_integration(self, queue_manager, starvation_prevention):
        """Test error handling across integrated components."""
        # Test invalid kitchen ID
        invalid_item = QueueItem(
            item_id="INVALID_TEST",
            item_name="Invalid Test",
            order_id="INVALID_ORDER",
            prep_time=15,
            scheduled_start=datetime.now(),
            estimated_completion=datetime.now() + timedelta(minutes=15),
            priority_level=PriorityLevel.NORMAL,
            starvation_count=0,
            status=ItemStatus.QUEUED,
            kitchen_id="INVALID_KITCHEN"
        )
        
        # Should handle gracefully
        success = queue_manager.add_item_to_queue("INVALID_KITCHEN", invalid_item)
        assert success is False
        
        # Test starvation prevention with non-existent item
        result = starvation_prevention.apply_emergency_priority("NON_EXISTENT_ITEM")
        assert result["applied"] is False
        
        # Test queue operations with non-existent items
        success = queue_manager.remove_completed_item("KITCHEN_A", "NON_EXISTENT")
        assert success is False
        
        success = queue_manager.update_item_status("KITCHEN_A", "NON_EXISTENT", ItemStatus.IN_PROGRESS)
        assert success is False
