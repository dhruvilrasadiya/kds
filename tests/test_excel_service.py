"""
Unit tests for ExcelDataService.
"""

import pytest
import pandas as pd
from datetime import datetime

from app.services.excel_service import ExcelDataService


class TestExcelDataService:
    """Test cases for ExcelDataService."""
    
    def test_load_kitchen_config(self, excel_service):
        """Test loading kitchen configuration."""
        kitchens = excel_service.load_kitchen_config()
        
        assert isinstance(kitchens, dict)
        assert len(kitchens) == 3
        assert "KITCHEN_A" in kitchens
        assert "KITCHEN_B" in kitchens
        assert "KITCHEN_C" in kitchens
        
        kitchen_a = kitchens["KITCHEN_A"]
        assert kitchen_a["kitchen_name"] == "Grill Station"
        assert kitchen_a["capacity"] == 3
        assert kitchen_a["specialization"] == "Grilled Items"
        assert kitchen_a["status"] == "active"
    
    def test_load_menu_items(self, excel_service):
        """Test loading menu items."""
        items = excel_service.load_menu_items()
        
        assert isinstance(items, dict)
        assert len(items) >= 3
        
        # Check specific items
        assert "ITM_001" in items
        item_001 = items["ITM_001"]
        assert item_001["item_name"] == "Grilled Chicken"
        assert item_001["kitchen_id"] == "KITCHEN_A"
        assert item_001["prep_time_minutes"] == 15
        assert item_001["available"] is True
    
    def test_load_historical_data(self, excel_service):
        """Test loading historical performance data."""
        historical_data = excel_service.load_historical_data()
        
        assert isinstance(historical_data, pd.DataFrame)
        assert len(historical_data) > 0
        
        # Check required columns
        required_columns = [
            'date', 'kitchen_id', 'item_id', 'actual_prep_time',
            'scheduled_prep_time', 'delay_minutes', 'kitchen_load', 'order_id'
        ]
        for col in required_columns:
            assert col in historical_data.columns
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(historical_data['date'])
    
    def test_load_kitchen_load_patterns(self, excel_service):
        """Test loading kitchen load patterns."""
        patterns = excel_service.load_kitchen_load_patterns()
        
        assert isinstance(patterns, pd.DataFrame)
        assert len(patterns) == 24  # 24 hours
        
        # Check required columns
        required_columns = [
            'hour', 'kitchen_a_avg_load', 'kitchen_b_avg_load', 'kitchen_c_avg_load'
        ]
        for col in required_columns:
            assert col in patterns.columns
        
        # Check hour range
        assert patterns['hour'].min() == 0
        assert patterns['hour'].max() == 23
    
    def test_validate_order_items_valid(self, excel_service):
        """Test validating valid order items."""
        valid_items = ["ITM_001", "ITM_004", "ITM_007"]
        result = excel_service.validate_order_items(valid_items)
        assert result is True
    
    def test_validate_order_items_invalid(self, excel_service):
        """Test validating invalid order items."""
        invalid_items = ["ITM_001", "INVALID_ITEM", "ITM_007"]
        result = excel_service.validate_order_items(invalid_items)
        assert result is False
    
    def test_get_item_by_id(self, excel_service):
        """Test getting item by ID."""
        item = excel_service.get_item_by_id("ITM_001")
        
        assert item is not None
        assert item["item_id"] == "ITM_001"
        assert item["item_name"] == "Grilled Chicken"
        
        # Test non-existent item
        non_existent = excel_service.get_item_by_id("NON_EXISTENT")
        assert non_existent is None
    
    def test_get_items_by_kitchen(self, excel_service):
        """Test getting items by kitchen."""
        kitchen_a_items = excel_service.get_items_by_kitchen("KITCHEN_A")
        
        assert isinstance(kitchen_a_items, list)
        assert len(kitchen_a_items) > 0
        
        # All items should belong to KITCHEN_A
        for item in kitchen_a_items:
            assert item["kitchen_id"] == "KITCHEN_A"
    
    def test_get_kitchen_by_id(self, excel_service):
        """Test getting kitchen by ID."""
        kitchen = excel_service.get_kitchen_by_id("KITCHEN_A")
        
        assert kitchen is not None
        assert kitchen["kitchen_id"] == "KITCHEN_A"
        assert kitchen["kitchen_name"] == "Grill Station"
        
        # Test non-existent kitchen
        non_existent = excel_service.get_kitchen_by_id("NON_EXISTENT")
        assert non_existent is None
    
    def test_update_historical_performance(self, excel_service):
        """Test updating historical performance data."""
        performance_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'kitchen_id': 'KITCHEN_A',
            'item_id': 'ITM_001',
            'order_id': 'TEST_ORDER',
            'actual_prep_time': 16,
            'scheduled_prep_time': 15,
            'delay_minutes': 1,
            'kitchen_load': 2
        }
        
        # This should not raise an exception
        excel_service.update_historical_performance(performance_data)
        
        # Verify data was added
        historical_data = excel_service.load_historical_data()
        assert len(historical_data) > 0
    
    def test_clear_cache(self, excel_service):
        """Test clearing cache."""
        # Load data to populate cache
        excel_service.load_kitchen_config()
        excel_service.load_menu_items()
        
        # Clear cache
        excel_service.clear_cache()
        
        # This should work without issues (cache will be repopulated)
        kitchens = excel_service.load_kitchen_config()
        assert len(kitchens) == 3
    
    def test_file_not_found_handling(self):
        """Test handling of missing Excel file."""
        # Create service with non-existent file
        service = ExcelDataService("non_existent_file.xlsx")
        
        # Should create sample file and work
        kitchens = service.load_kitchen_config()
        assert isinstance(kitchens, dict)
        assert len(kitchens) > 0
