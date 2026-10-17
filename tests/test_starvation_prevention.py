"""
Unit tests for StarvationPrevention.
"""

import pytest
from datetime import datetime, timedelta

from app.services.starvation_prevention import StarvationPrevention
from app.models import PriorityLevel


class TestStarvationPrevention:
    """Test cases for StarvationPrevention."""
    
    def test_initialization(self, starvation_prevention):
        """Test starvation prevention initialization."""
        assert starvation_prevention.max_delays == 3
        assert len(starvation_prevention.item_delay_counter) == 0
        assert len(starvation_prevention.emergency_items) == 0
    
    def test_increment_delay_counter(self, starvation_prevention):
        """Test incrementing delay counter."""
        item_id = "TEST_ITEM"
        
        # First delay
        starvation_prevention.increment_delay_counter(item_id)
        assert starvation_prevention.item_delay_counter[item_id] == 1
        assert item_id in starvation_prevention.item_first_delay_time
        
        # Second delay
        starvation_prevention.increment_delay_counter(item_id)
        assert starvation_prevention.item_delay_counter[item_id] == 2
    
    def test_check_starvation(self, starvation_prevention):
        """Test starvation checking."""
        item_id = "TEST_ITEM"
        
        # Initially not starving
        assert starvation_prevention.check_starvation(item_id) is False
        
        # Add delays up to threshold
        for i in range(3):
            starvation_prevention.increment_delay_counter(item_id)
        
        # Should be starving now
        assert starvation_prevention.check_starvation(item_id) is True
        assert item_id in starvation_prevention.emergency_items
    
    def test_apply_emergency_priority(self, starvation_prevention):
        """Test applying emergency priority."""
        item_id = "TEST_ITEM"
        
        # Make item starving
        for i in range(3):
            starvation_prevention.increment_delay_counter(item_id)
        
        # Apply emergency priority
        result = starvation_prevention.apply_emergency_priority(item_id)
        
        assert result["applied"] is True
        assert result["config"]["priority"] == PriorityLevel.EMERGENCY
        assert result["config"]["force_schedule"] is True
        assert result["delay_count"] == 3
    
    def test_apply_emergency_priority_non_starving(self, starvation_prevention):
        """Test applying emergency priority to non-starving item."""
        item_id = "TEST_ITEM"
        
        # Try to apply emergency priority without starvation
        result = starvation_prevention.apply_emergency_priority(item_id)
        
        assert result["applied"] is False
        assert result["reason"] == "item_not_starving"
    
    def test_reset_item_counters(self, starvation_prevention):
        """Test resetting item counters."""
        item_id = "TEST_ITEM"
        
        # Make item starving
        for i in range(3):
            starvation_prevention.increment_delay_counter(item_id)
        
        assert item_id in starvation_prevention.item_delay_counter
        assert item_id in starvation_prevention.emergency_items
        
        # Reset counters
        starvation_prevention.reset_item_counters(item_id)
        
        assert item_id not in starvation_prevention.item_delay_counter
        assert item_id not in starvation_prevention.emergency_items
        assert item_id not in starvation_prevention.item_first_delay_time
    
    def test_get_starving_items(self, starvation_prevention):
        """Test getting starving items."""
        # Initially empty
        starving = starvation_prevention.get_starving_items()
        assert len(starving) == 0
        
        # Make items starving
        items = ["ITEM_1", "ITEM_2"]
        for item_id in items:
            for i in range(3):
                starvation_prevention.increment_delay_counter(item_id)
        
        starving = starvation_prevention.get_starving_items()
        assert len(starving) == 2
        assert "ITEM_1" in starving
        assert "ITEM_2" in starving
    
    def test_get_item_delay_info(self, starvation_prevention):
        """Test getting item delay information."""
        item_id = "TEST_ITEM"
        
        # Initially no delays
        info = starvation_prevention.get_item_delay_info(item_id)
        assert info["delay_count"] == 0
        assert info["is_starving"] is False
        assert info["is_emergency"] is False
        
        # Add delays
        starvation_prevention.increment_delay_counter(item_id)
        starvation_prevention.increment_delay_counter(item_id)
        
        info = starvation_prevention.get_item_delay_info(item_id)
        assert info["delay_count"] == 2
        assert info["is_starving"] is False
        assert info["first_delay_time"] is not None
        assert info["time_since_first_delay"] is not None
    
    def test_get_starvation_statistics(self, starvation_prevention):
        """Test getting starvation statistics."""
        # Add some delayed items
        items = ["ITEM_1", "ITEM_2", "ITEM_3"]
        
        # ITEM_1: 1 delay
        starvation_prevention.increment_delay_counter(items[0])
        
        # ITEM_2: 2 delays
        for i in range(2):
            starvation_prevention.increment_delay_counter(items[1])
        
        # ITEM_3: 3 delays (starving)
        for i in range(3):
            starvation_prevention.increment_delay_counter(items[2])
        
        stats = starvation_prevention.get_starvation_statistics()
        
        assert stats["total_delayed_items"] == 3
        assert stats["currently_starving"] == 1
        assert stats["max_delays_threshold"] == 3
        assert stats["average_delay_count"] == 2.0  # (1+2+3)/3
        assert items[2] in stats["emergency_items"]
    
    def test_apply_starvation_boost_to_queue_item(self, starvation_prevention, sample_queue_item):
        """Test applying starvation boost to queue item."""
        # Make item starving
        for i in range(3):
            starvation_prevention.increment_delay_counter(sample_queue_item.item_id)
        
        # Apply boost
        boosted_item = starvation_prevention.apply_starvation_boost_to_queue_item(sample_queue_item)
        
        assert boosted_item.priority_level == PriorityLevel.EMERGENCY
        assert boosted_item.starvation_count == 3
        assert boosted_item.scheduled_start <= datetime.now()
    
    def test_should_bypass_optimization(self, starvation_prevention):
        """Test bypass optimization check."""
        item_id = "TEST_ITEM"
        
        # Initially should not bypass
        assert starvation_prevention.should_bypass_optimization(item_id) is False
        
        # Make starving
        for i in range(3):
            starvation_prevention.increment_delay_counter(item_id)
        
        # Should bypass now
        assert starvation_prevention.should_bypass_optimization(item_id) is True
    
    def test_get_priority_boost_factor(self, starvation_prevention):
        """Test priority boost factor calculation."""
        item_id = "TEST_ITEM"
        
        # No delays
        factor = starvation_prevention.get_priority_boost_factor(item_id)
        assert factor == 1.0
        
        # One delay
        starvation_prevention.increment_delay_counter(item_id)
        factor = starvation_prevention.get_priority_boost_factor(item_id)
        assert factor == 1.2  # 1.0 + (1 * 0.2)
        
        # Two delays
        starvation_prevention.increment_delay_counter(item_id)
        factor = starvation_prevention.get_priority_boost_factor(item_id)
        assert factor == 1.4  # 1.0 + (2 * 0.2)
        
        # Starving (3+ delays)
        starvation_prevention.increment_delay_counter(item_id)
        factor = starvation_prevention.get_priority_boost_factor(item_id)
        assert factor == 3.0  # Maximum boost
    
    def test_cleanup_old_entries(self, starvation_prevention):
        """Test cleanup of old entries."""
        item_id = "OLD_ITEM"
        
        # Add delay and manually set old timestamp
        starvation_prevention.increment_delay_counter(item_id)
        old_time = datetime.now() - timedelta(hours=25)
        starvation_prevention.item_first_delay_time[item_id] = old_time
        
        # Cleanup
        starvation_prevention.cleanup_old_entries(24)
        
        # Item should be removed
        assert item_id not in starvation_prevention.item_delay_counter
        assert item_id not in starvation_prevention.item_first_delay_time
        assert item_id not in starvation_prevention.emergency_items
    
    def test_starvation_history_tracking(self, starvation_prevention):
        """Test starvation history tracking."""
        item_id = "TEST_ITEM"
        
        # Make item starving
        for i in range(3):
            starvation_prevention.increment_delay_counter(item_id)
        
        # Should have recorded starvation event
        assert len(starvation_prevention.starvation_history) > 0
        
        # Apply emergency priority
        starvation_prevention.apply_emergency_priority(item_id)
        
        # Should have recorded intervention
        intervention_events = [
            event for event in starvation_prevention.starvation_history
            if event.get("event_type") == "emergency_intervention"
        ]
        assert len(intervention_events) > 0
