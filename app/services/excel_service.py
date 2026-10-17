"""
Excel Data Management Service for the Smart Kitchen Queue Management System.
"""

import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime
import os
from app.config import config

logger = logging.getLogger(__name__)


class ExcelDataService:
    """Service for managing Excel-based configuration and historical data."""
    
    def __init__(self, excel_file_path: Optional[str] = None):
        """Initialize the Excel data service."""
        self.excel_file_path = excel_file_path or config.EXCEL_FILE_PATH
        self._kitchens_cache = None
        self._items_cache = None
        self._historical_cache = None
        self._load_patterns_cache = None
        
    def _ensure_file_exists(self) -> bool:
        """Ensure the Excel file exists, create sample if not."""
        if not os.path.exists(self.excel_file_path):
            logger.warning(f"Excel file not found at {self.excel_file_path}")
            try:
                from app.utils.excel_creator import create_sample_excel
                create_sample_excel(self.excel_file_path)
                logger.info(f"Created sample Excel file at {self.excel_file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to create sample Excel file: {e}")
                return False
        return True
    
    def load_kitchen_config(self) -> Dict:
        """Load kitchen configuration from Excel."""
        if not self._ensure_file_exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")
        
        try:
            if self._kitchens_cache is None:
                df = pd.read_excel(self.excel_file_path, sheet_name='kitchens')
                self._kitchens_cache = {}
                
                for _, row in df.iterrows():
                    kitchen_id = row['kitchen_id']
                    self._kitchens_cache[kitchen_id] = {
                        'kitchen_id': kitchen_id,
                        'kitchen_name': row['kitchen_name'],  # Keep original for queue manager
                        'name': row['kitchen_name'],  # Also add for frontend compatibility
                        'capacity': int(row['capacity']),
                        'specialization': row['specialization'],
                        'status': row.get('status', 'active'),
                        'current_load': int(row.get('current_load', 0)),
                        'staff_count': int(row.get('staff_count', 1))
                    }
                
                logger.info(f"Loaded {len(self._kitchens_cache)} kitchens from Excel")
            
            return self._kitchens_cache
            
        except Exception as e:
            logger.error(f"Error loading kitchen config: {e}")
            raise
    
    def load_menu_items(self) -> Dict:
        """Load menu items from Excel."""
        if not self._ensure_file_exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")
        
        try:
            if self._items_cache is None:
                df = pd.read_excel(self.excel_file_path, sheet_name='items')
                self._items_cache = {}
                
                for _, row in df.iterrows():
                    item_id = str(row['item_id'])  # Convert to string to match frontend
                    self._items_cache[item_id] = {
                        'item_id': item_id,
                        'item_name': row['item_name'],  # Keep original field name for AI agent
                        'name': row['item_name'],  # Also add for frontend compatibility
                        'kitchen_id': row['kitchen_id'],
                        'prep_time_minutes': int(row['prep_time_minutes']),  # Keep original field name for AI agent
                        'prep_time': int(row['prep_time_minutes']),  # Also add for frontend compatibility
                        'difficulty': row['difficulty_level'],  # Changed to match frontend
                        'description': row.get('description', ''),
                        'price': float(row.get('price', 0.0)),
                        'image': row.get('image', '/placeholder.svg'),
                        'calories': int(row.get('calories', 0)),
                        'category': row.get('category', 'other'),
                        'available': bool(row.get('available', True))
                    }
                
                logger.info(f"Loaded {len(self._items_cache)} menu items from Excel")
            
            return self._items_cache
            
        except Exception as e:
            logger.error(f"Error loading menu items: {e}")
            raise
    
    def load_historical_data(self) -> pd.DataFrame:
        """Load historical performance data from Excel."""
        if not self._ensure_file_exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")
        
        try:
            if self._historical_cache is None:
                self._historical_cache = pd.read_excel(
                    self.excel_file_path, 
                    sheet_name='historical_performance'
                )
                
                # Convert date column to datetime
                self._historical_cache['date'] = pd.to_datetime(self._historical_cache['date'])
                
                logger.info(f"Loaded {len(self._historical_cache)} historical records from Excel")
            
            return self._historical_cache.copy()
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            raise
    
    def load_kitchen_load_patterns(self) -> pd.DataFrame:
        """Load kitchen load patterns from Excel."""
        if not self._ensure_file_exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")
        
        try:
            if self._load_patterns_cache is None:
                self._load_patterns_cache = pd.read_excel(
                    self.excel_file_path, 
                    sheet_name='kitchen_load_patterns'
                )
                
                logger.info(f"Loaded kitchen load patterns from Excel")
            
            return self._load_patterns_cache.copy()
            
        except Exception as e:
            logger.error(f"Error loading kitchen load patterns: {e}")
            raise

    def validate_order_items(self, items: List[str]) -> bool:
        """Validate that all items in an order exist and are available."""
        try:
            menu_items = self.load_menu_items()

            for item_id in items:
                if item_id not in menu_items:
                    logger.warning(f"Item {item_id} not found in menu")
                    return False

                if not menu_items[item_id]['available']:
                    logger.warning(f"Item {item_id} is not available")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating order items: {e}")
            return False

    def update_historical_performance(self, performance_data: Dict):
        """Update historical performance data in Excel."""
        try:
            # Load existing data
            historical_df = self.load_historical_data()

            # Create new record
            new_record = pd.DataFrame([performance_data])

            # Append to existing data
            updated_df = pd.concat([historical_df, new_record], ignore_index=True)

            # Write back to Excel
            with pd.ExcelWriter(self.excel_file_path, mode='a', if_sheet_exists='replace') as writer:
                updated_df.to_excel(writer, sheet_name='historical_performance', index=False)

            # Clear cache to force reload
            self._historical_cache = None

            logger.info(f"Updated historical performance data")

        except Exception as e:
            logger.error(f"Error updating historical performance: {e}")
            raise

    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get a specific item by ID."""
        menu_items = self.load_menu_items()
        return menu_items.get(item_id)

    def get_items_by_kitchen(self, kitchen_id: str) -> List[Dict]:
        """Get all items for a specific kitchen."""
        menu_items = self.load_menu_items()
        return [item for item in menu_items.values() if item['kitchen_id'] == kitchen_id]

    def get_kitchen_by_id(self, kitchen_id: str) -> Optional[Dict]:
        """Get a specific kitchen by ID."""
        kitchens = self.load_kitchen_config()
        return kitchens.get(kitchen_id)

    def clear_cache(self):
        """Clear all cached data to force reload from Excel."""
        self._kitchens_cache = None
        self._items_cache = None
        self._historical_cache = None
        self._load_patterns_cache = None
        logger.info("Excel data cache cleared")
