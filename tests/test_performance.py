"""
Performance tests for the Smart Kitchen Queue Management System.
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.models import QueueItem, PriorityLevel, ItemStatus


class TestPerformance:
    """Performance test cases."""
    
    def test_queue_manager_scalability(self, queue_manager, test_utils):
        """Test queue manager performance with large number of items."""
        kitchen_id = "KITCHEN_A"
        num_items = 1000
        
        # Measure time to add items
        start_time = time.time()
        
        items = test_utils.create_test_queue_items(num_items, kitchen_id)
        for i, item in enumerate(items):
            item.item_id = f"PERF_ITEM_{i:04d}"
            # Only add items up to capacity to avoid failures
            if i < 100:  # Reasonable number for testing
                queue_manager.add_item_to_queue(kitchen_id, item)
        
        add_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert add_time < 5.0, f"Adding 100 items took {add_time:.2f} seconds"
        
        # Measure time to get kitchen status
        start_time = time.time()
        status = queue_manager.get_kitchen_status(kitchen_id)
        status_time = time.time() - start_time
        
        assert status_time < 0.1, f"Getting kitchen status took {status_time:.2f} seconds"
        assert status is not None
    
    def test_concurrent_queue_operations(self, queue_manager, test_utils):
        """Test concurrent operations on queue manager."""
        kitchen_id = "KITCHEN_A"
        num_threads = 10
        items_per_thread = 5
        
        def add_items_worker(thread_id):
            """Worker function to add items concurrently."""
            items = test_utils.create_test_queue_items(items_per_thread, kitchen_id)
            results = []
            
            for i, item in enumerate(items):
                item.item_id = f"THREAD_{thread_id}_ITEM_{i}"
                try:
                    success = queue_manager.add_item_to_queue(kitchen_id, item)
                    results.append(success)
                except Exception as e:
                    results.append(False)
            
            return results
        
        # Run concurrent operations
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(add_items_worker, thread_id)
                for thread_id in range(num_threads)
            ]
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        execution_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert execution_time < 10.0, f"Concurrent operations took {execution_time:.2f} seconds"
        
        # Check that some operations succeeded (capacity limits may cause some failures)
        success_count = sum(all_results)
        assert success_count > 0, "No operations succeeded"
        
        # Verify queue integrity
        status = queue_manager.get_kitchen_status(kitchen_id)
        assert status is not None
        assert len(status.current_queue) == success_count
    
    def test_starvation_prevention_performance(self, starvation_prevention):
        """Test starvation prevention performance with many items."""
        num_items = 1000
        
        # Measure time to process delays for many items
        start_time = time.time()
        
        for i in range(num_items):
            item_id = f"PERF_ITEM_{i:04d}"
            # Add varying number of delays
            for j in range(i % 5):
                starvation_prevention.increment_delay_counter(item_id)
        
        delay_processing_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert delay_processing_time < 5.0, f"Processing delays took {delay_processing_time:.2f} seconds"
        
        # Measure time to get statistics
        start_time = time.time()
        stats = starvation_prevention.get_starvation_statistics()
        stats_time = time.time() - start_time
        
        assert stats_time < 1.0, f"Getting statistics took {stats_time:.2f} seconds"
        assert stats["total_delayed_items"] == num_items
    
    def test_concurrent_starvation_operations(self, starvation_prevention):
        """Test concurrent starvation prevention operations."""
        num_threads = 20
        operations_per_thread = 50
        
        def starvation_worker(thread_id):
            """Worker function for starvation operations."""
            results = []
            
            for i in range(operations_per_thread):
                item_id = f"THREAD_{thread_id}_ITEM_{i}"
                
                try:
                    # Increment delay counter
                    starvation_prevention.increment_delay_counter(item_id)
                    
                    # Check starvation status
                    is_starving = starvation_prevention.check_starvation(item_id)
                    
                    # Get delay info
                    delay_info = starvation_prevention.get_item_delay_info(item_id)
                    
                    results.append(True)
                    
                except Exception as e:
                    results.append(False)
            
            return results
        
        # Run concurrent operations
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(starvation_worker, thread_id)
                for thread_id in range(num_threads)
            ]
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        execution_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert execution_time < 10.0, f"Concurrent starvation operations took {execution_time:.2f} seconds"
        
        # All operations should succeed
        success_count = sum(all_results)
        total_operations = num_threads * operations_per_thread
        assert success_count == total_operations, f"Only {success_count}/{total_operations} operations succeeded"
    
    def test_memory_usage_stability(self, queue_manager, starvation_prevention, test_utils):
        """Test memory usage stability over time."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for cycle in range(10):
            # Add items
            items = test_utils.create_test_queue_items(50, "KITCHEN_A")
            for i, item in enumerate(items):
                item.item_id = f"CYCLE_{cycle}_ITEM_{i:02d}"
                if queue_manager.check_kitchen_capacity("KITCHEN_A"):
                    queue_manager.add_item_to_queue("KITCHEN_A", item)
            
            # Process starvation
            for i in range(20):
                item_id = f"CYCLE_{cycle}_STARV_{i:02d}"
                starvation_prevention.increment_delay_counter(item_id)
            
            # Complete some items
            status = queue_manager.get_kitchen_status("KITCHEN_A")
            if status and status.current_queue:
                for item in status.current_queue[:10]:  # Complete first 10 items
                    queue_manager.remove_completed_item("KITCHEN_A", item.item_id)
            
            # Clean up
            queue_manager.clear_completed_items("KITCHEN_A", 0)
            starvation_prevention.cleanup_old_entries(0)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        max_increase = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_increase, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"
    
    def test_queue_reordering_performance(self, queue_manager, test_utils):
        """Test performance of queue reordering operations."""
        kitchen_id = "KITCHEN_A"
        num_items = 200
        
        # Create items with random priorities
        items = test_utils.create_test_queue_items(num_items, kitchen_id)
        priorities = [PriorityLevel.LOW, PriorityLevel.NORMAL, PriorityLevel.HIGH, PriorityLevel.EMERGENCY]
        
        for i, item in enumerate(items):
            item.item_id = f"REORDER_ITEM_{i:03d}"
            item.priority_level = priorities[i % len(priorities)]
            # Add only a reasonable number to avoid capacity issues
            if i < 50:
                queue_manager.add_item_to_queue(kitchen_id, item)
        
        # Measure reordering time
        start_time = time.time()
        queue_manager.reorder_queue_by_priority(kitchen_id)
        reorder_time = time.time() - start_time
        
        # Should complete quickly
        assert reorder_time < 1.0, f"Queue reordering took {reorder_time:.2f} seconds"
        
        # Verify queue is properly ordered
        status = queue_manager.get_kitchen_status(kitchen_id)
        queue = status.current_queue
        
        # Check that emergency items come first
        emergency_items = [item for item in queue if item.priority_level == PriorityLevel.EMERGENCY]
        if emergency_items:
            # Find first emergency item index
            first_emergency_index = next(
                i for i, item in enumerate(queue) 
                if item.priority_level == PriorityLevel.EMERGENCY
            )
            
            # All items before first emergency should not be lower priority
            for i in range(first_emergency_index):
                assert queue[i].priority_level in [PriorityLevel.EMERGENCY, PriorityLevel.HIGH]
    
    def test_bulk_completion_performance(self, queue_manager, test_utils):
        """Test performance of bulk item completion."""
        kitchen_id = "KITCHEN_A"
        num_items = 100
        
        # Add items
        items = test_utils.create_test_queue_items(num_items, kitchen_id)
        added_items = []
        
        for i, item in enumerate(items):
            item.item_id = f"BULK_ITEM_{i:03d}"
            if queue_manager.check_kitchen_capacity(kitchen_id):
                success = queue_manager.add_item_to_queue(kitchen_id, item)
                if success:
                    added_items.append(item)
        
        # Measure bulk completion time
        start_time = time.time()
        
        for item in added_items:
            queue_manager.remove_completed_item(kitchen_id, item.item_id)
        
        completion_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert completion_time < 2.0, f"Bulk completion took {completion_time:.2f} seconds"
        
        # Verify all items are completed
        status = queue_manager.get_kitchen_status(kitchen_id)
        completed_items = [item for item in status.current_queue if item.status == ItemStatus.COMPLETED]
        assert len(completed_items) == len(added_items)
    
    def test_system_responsiveness_under_load(self, queue_manager, starvation_prevention, test_utils):
        """Test system responsiveness under high load."""
        def background_load():
            """Generate background load."""
            for i in range(100):
                # Queue operations
                item = test_utils.create_test_queue_items(1, "KITCHEN_B")[0]
                item.item_id = f"BG_ITEM_{i:03d}"
                if queue_manager.check_kitchen_capacity("KITCHEN_B"):
                    queue_manager.add_item_to_queue("KITCHEN_B", item)
                
                # Starvation operations
                starvation_prevention.increment_delay_counter(f"BG_STARV_{i:03d}")
                
                time.sleep(0.01)  # Small delay to simulate real workload
        
        # Start background load
        background_thread = threading.Thread(target=background_load, daemon=True)
        background_thread.start()
        
        # Measure response times for critical operations
        response_times = []
        
        for i in range(20):
            start_time = time.time()
            
            # Critical operation: get kitchen status
            status = queue_manager.get_kitchen_status("KITCHEN_A")
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            time.sleep(0.1)  # Wait between measurements
        
        # Wait for background thread to complete
        background_thread.join(timeout=15)
        
        # Analyze response times
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Response times should remain reasonable under load
        assert avg_response_time < 0.1, f"Average response time: {avg_response_time:.3f}s"
        assert max_response_time < 0.5, f"Max response time: {max_response_time:.3f}s"
