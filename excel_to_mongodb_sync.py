#!/usr/bin/env python3
"""
Excel to MongoDB Data Migration Script (Synchronous Version)
===========================================================

This is a simpler synchronous version of the Excel to MongoDB migration script.
It uses pymongo instead of motor for easier usage.

Usage:
    python excel_to_mongodb_sync.py [options]

Requirements:
    pip install pandas openpyxl pymongo
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ExcelToMongoMigratorSync:
    """Synchronous version of Excel to MongoDB migrator."""
    
    def __init__(self, excel_file: str, mongodb_url: str, database_name: str):
        self.excel_file = excel_file
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.db = None
        
    def connect_mongodb(self) -> bool:
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            return False
    
    def disconnect_mongodb(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")
    
    def validate_excel_file(self) -> bool:
        """Validate that the Excel file exists and has required sheets."""
        if not os.path.exists(self.excel_file):
            logger.error(f"❌ Excel file not found: {self.excel_file}")
            return False
        
        try:
            # Check for required sheets
            excel_file = pd.ExcelFile(self.excel_file)
            required_sheets = ['items', 'kitchens']
            missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
            
            if missing_sheets:
                logger.error(f"❌ Missing required sheets: {missing_sheets}")
                logger.info(f"Available sheets: {excel_file.sheet_names}")
                return False
            
            logger.info(f"✅ Excel file validated: {self.excel_file}")
            logger.info(f"Available sheets: {excel_file.sheet_names}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating Excel file: {e}")
            return False
    
    def load_menu_items(self) -> List[Dict[str, Any]]:
        """Load menu items from Excel."""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='items')
            logger.info(f"📋 Loaded {len(df)} menu items from Excel")
            
            menu_items = []
            for _, row in df.iterrows():
                item = {
                    "item_id": str(row['item_id']),  # Ensure string format
                    "item_name": row['item_name'],
                    "name": row['item_name'],  # Compatibility field
                    "kitchen_id": row['kitchen_id'],
                    "prep_time_minutes": int(row['prep_time_minutes']),
                    "prep_time": int(row['prep_time_minutes']),  # Compatibility field
                    "difficulty_level": row.get('difficulty_level', 'medium'),
                    "difficulty": row.get('difficulty_level', 'medium'),  # Compatibility field
                    "category": row.get('category', 'general'),
                    "description": row.get('description', ''),
                    "price": float(row.get('price', 0.0)),
                    "available": bool(row.get('available', True)),
                    "image": row.get('image', '/placeholder.svg'),
                    "calories": int(row.get('calories', 0)),
                    "allergens": row.get('allergens', '').split(',') if row.get('allergens') else [],
                    "nutritional_info": {
                        "calories": int(row.get('calories', 0)),
                        "protein": row.get('protein', ''),
                        "carbs": row.get('carbs', ''),
                        "fat": row.get('fat', '')
                    },
                    "sync_source": "excel_migration",
                    "synced_at": datetime.now(),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                menu_items.append(item)
            
            return menu_items
            
        except Exception as e:
            logger.error(f"❌ Error loading menu items: {e}")
            return []
    
    def load_kitchens(self) -> List[Dict[str, Any]]:
        """Load kitchens from Excel."""
        try:
            df = pd.read_excel(self.excel_file, sheet_name='kitchens')
            logger.info(f"🏪 Loaded {len(df)} kitchens from Excel")
            
            kitchens = []
            for _, row in df.iterrows():
                kitchen = {
                    "kitchen_id": row['kitchen_id'],
                    "kitchen_name": row['kitchen_name'],
                    "name": row['kitchen_name'],  # Compatibility field
                    "capacity": int(row['capacity']),
                    "specialization": row.get('specialization', 'general'),
                    "status": row.get('status', 'active'),
                    "current_load": int(row.get('current_load', 0)),
                    "staff_count": int(row.get('staff_count', 1)),
                    "equipment": row.get('equipment', '').split(',') if row.get('equipment') else [],
                    "sync_source": "excel_migration",
                    "synced_at": datetime.now(),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                kitchens.append(kitchen)
            
            return kitchens
            
        except Exception as e:
            logger.error(f"❌ Error loading kitchens: {e}")
            return []
    
    def create_indexes(self):
        """Create MongoDB indexes for optimal performance."""
        try:
            # Menu items indexes
            self.db.menu_items.create_index("item_id", unique=True)
            self.db.menu_items.create_index("category")
            self.db.menu_items.create_index("available")
            self.db.menu_items.create_index("kitchen_id")
            
            # Kitchen indexes
            self.db.kitchens.create_index("kitchen_id", unique=True)
            self.db.kitchens.create_index("status")
            
            # Orders indexes (for future use)
            self.db.orders.create_index("order_id", unique=True)
            self.db.orders.create_index("status")
            self.db.orders.create_index("timestamp")
            
            # Queue items indexes (for future use)
            self.db.queue_items.create_index("queue_id", unique=True)
            self.db.queue_items.create_index("order_id")
            self.db.queue_items.create_index("kitchen_id")
            self.db.queue_items.create_index("status")
            
            logger.info("✅ MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    def clear_existing_data(self):
        """Clear existing data from MongoDB collections."""
        try:
            collections = ['menu_items', 'kitchens', 'orders', 'queue_items']
            
            for collection_name in collections:
                result = self.db[collection_name].delete_many({})
                logger.info(f"🗑️ Cleared {result.deleted_count} documents from {collection_name}")
            
            logger.info("✅ Existing data cleared successfully")
            
        except Exception as e:
            logger.error(f"❌ Error clearing existing data: {e}")
    
    def import_menu_items(self, menu_items: List[Dict[str, Any]], dry_run: bool = False) -> int:
        """Import menu items to MongoDB."""
        if not menu_items:
            logger.warning("⚠️ No menu items to import")
            return 0
        
        if dry_run:
            logger.info(f"🔍 DRY RUN: Would import {len(menu_items)} menu items")
            for item in menu_items[:3]:  # Show first 3 items
                logger.info(f"   - {item['item_id']}: {item['item_name']}")
            if len(menu_items) > 3:
                logger.info(f"   ... and {len(menu_items) - 3} more items")
            return len(menu_items)
        
        try:
            imported_count = 0
            for item in menu_items:
                try:
                    # Use replace_one with upsert=True for upsert behavior
                    result = self.db.menu_items.replace_one(
                        {"item_id": item["item_id"]},
                        item,
                        upsert=True
                    )
                    if result.upserted_id or result.modified_count > 0:
                        imported_count += 1
                except DuplicateKeyError:
                    # Handle duplicate key error by updating
                    self.db.menu_items.update_one(
                        {"item_id": item["item_id"]},
                        {"$set": item}
                    )
                    imported_count += 1
            
            logger.info(f"✅ Imported {imported_count} menu items")
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Error importing menu items: {e}")
            return 0
    
    def import_kitchens(self, kitchens: List[Dict[str, Any]], dry_run: bool = False) -> int:
        """Import kitchens to MongoDB."""
        if not kitchens:
            logger.warning("⚠️ No kitchens to import")
            return 0
        
        if dry_run:
            logger.info(f"🔍 DRY RUN: Would import {len(kitchens)} kitchens")
            for kitchen in kitchens:
                logger.info(f"   - {kitchen['kitchen_id']}: {kitchen['kitchen_name']}")
            return len(kitchens)
        
        try:
            imported_count = 0
            for kitchen in kitchens:
                try:
                    # Use replace_one with upsert=True for upsert behavior
                    result = self.db.kitchens.replace_one(
                        {"kitchen_id": kitchen["kitchen_id"]},
                        kitchen,
                        upsert=True
                    )
                    if result.upserted_id or result.modified_count > 0:
                        imported_count += 1
                except DuplicateKeyError:
                    # Handle duplicate key error by updating
                    self.db.kitchens.update_one(
                        {"kitchen_id": kitchen["kitchen_id"]},
                        {"$set": kitchen}
                    )
                    imported_count += 1
            
            logger.info(f"✅ Imported {imported_count} kitchens")
            return imported_count
            
        except Exception as e:
            logger.error(f"❌ Error importing kitchens: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics of MongoDB collections."""
        try:
            stats = {}
            collections = ['menu_items', 'kitchens', 'orders', 'queue_items']
            
            for collection_name in collections:
                count = self.db[collection_name].count_documents({})
                stats[collection_name] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {}
    
    def migrate_data(self, clear_existing: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Main migration function."""
        logger.info("🚀 Starting Excel to MongoDB migration...")
        
        results = {
            "success": False,
            "menu_items_imported": 0,
            "kitchens_imported": 0,
            "errors": []
        }
        
        try:
            # Validate Excel file
            if not self.validate_excel_file():
                results["errors"].append("Excel file validation failed")
                return results
            
            # Connect to MongoDB
            if not self.connect_mongodb():
                results["errors"].append("MongoDB connection failed")
                return results
            
            # Clear existing data if requested
            if clear_existing and not dry_run:
                self.clear_existing_data()
            
            # Create indexes
            if not dry_run:
                self.create_indexes()
            
            # Load data from Excel
            logger.info("📊 Loading data from Excel...")
            menu_items = self.load_menu_items()
            kitchens = self.load_kitchens()
            
            if not menu_items and not kitchens:
                results["errors"].append("No data loaded from Excel")
                return results
            
            # Import data to MongoDB
            logger.info("💾 Importing data to MongoDB...")
            results["menu_items_imported"] = self.import_menu_items(menu_items, dry_run)
            results["kitchens_imported"] = self.import_kitchens(kitchens, dry_run)
            
            # Get final statistics
            if not dry_run:
                stats = self.get_collection_stats()
                logger.info("📊 Final MongoDB Statistics:")
                for collection, count in stats.items():
                    logger.info(f"   {collection}: {count} documents")
            
            results["success"] = True
            logger.info("🎉 Migration completed successfully!")
            
            return results
            
        except Exception as e:
            logger.error(f"💥 Migration failed: {e}")
            results["errors"].append(str(e))
            return results
        
        finally:
            self.disconnect_mongodb()


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Migrate data from Excel to MongoDB (Synchronous Version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python excel_to_mongodb_sync.py
    python excel_to_mongodb_sync.py --excel-file custom_data.xlsx
    python excel_to_mongodb_sync.py --clear-existing --verbose
    python excel_to_mongodb_sync.py --dry-run
        """
    )
    
    parser.add_argument(
        "--excel-file",
        default="data/kitchen_config.xlsx",
        help="Path to Excel file (default: data/kitchen_config.xlsx)"
    )
    
    parser.add_argument(
        "--mongodb-url",
        default="mongodb://admin:password123@127.0.0.1:27017/smart_kitchen?authSource=admin",
        help="MongoDB connection URL (default: mongodb://admin:password123@127.0.0.1:27017/smart_kitchen?authSource=admin)"
    )
    
    parser.add_argument(
        "--database",
        default="smart_kitchen",
        help="Database name (default: smart_kitchen)"
    )
    
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing data before import"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without actually importing"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print configuration
    logger.info("📋 Migration Configuration:")
    logger.info(f"   Excel file: {args.excel_file}")
    logger.info(f"   MongoDB URL: {args.mongodb_url}")
    logger.info(f"   Database: {args.database}")
    logger.info(f"   Clear existing: {args.clear_existing}")
    logger.info(f"   Dry run: {args.dry_run}")
    
    # Create migrator and run migration
    migrator = ExcelToMongoMigratorSync(args.excel_file, args.mongodb_url, args.database)
    results = migrator.migrate_data(args.clear_existing, args.dry_run)
    
    # Print results
    logger.info("\n" + "="*60)
    logger.info("📊 MIGRATION RESULTS")
    logger.info("="*60)
    
    if results["success"]:
        logger.info("✅ Status: SUCCESS")
        logger.info(f"📋 Menu items imported: {results['menu_items_imported']}")
        logger.info(f"🏪 Kitchens imported: {results['kitchens_imported']}")
        
        if args.dry_run:
            logger.info("\n🔍 This was a DRY RUN - no data was actually imported")
            logger.info("Run without --dry-run to perform the actual migration")
        else:
            logger.info("\n🎉 Data migration completed successfully!")
            logger.info("Your MongoDB database is now ready for the Smart Kitchen Queue Management System")
        
        sys.exit(0)
    else:
        logger.error("❌ Status: FAILED")
        logger.error("Errors:")
        for error in results["errors"]:
            logger.error(f"   - {error}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
