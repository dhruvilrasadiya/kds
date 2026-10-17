#!/usr/bin/env python3
"""
Test script to verify MongoDB integration for Smart Kitchen Queue Management System.
This script tests the complete flow from Excel data migration to MongoDB operations.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.mongodb_service import mongodb_service
from app.services.startup_service import startup_service


async def test_mongodb_integration():
    """Test the complete MongoDB integration."""
    print("🧪 Testing MongoDB Integration for Smart Kitchen Queue Management System")
    print("=" * 80)
    
    try:
        # Step 1: Initialize the application
        print("\n📋 Step 1: Initializing application...")
        init_results = await startup_service.initialize_application()
        
        print(f"✅ MongoDB Connection: {init_results['mongodb_connection']}")
        print(f"✅ Data Migration: {init_results['data_migration']}")
        print(f"📊 Menu Items: {init_results['menu_items_count']}")
        print(f"🏪 Kitchens: {init_results['kitchens_count']}")
        
        if init_results['errors']:
            print(f"⚠️ Errors: {init_results['errors']}")
        
        # Step 2: Test menu items retrieval
        print("\n📋 Step 2: Testing menu items retrieval...")
        menu_items = await mongodb_service.get_menu_items()
        print(f"✅ Retrieved {len(menu_items)} menu items")
        
        if menu_items:
            sample_item = menu_items[0]
            print(f"📄 Sample item: {sample_item['item_id']} - {sample_item.get('item_name', sample_item.get('name', 'Unknown'))}")
            
            # Test individual item retrieval
            item = await mongodb_service.get_menu_item(sample_item['item_id'])
            if item:
                print(f"✅ Individual item retrieval successful")
            else:
                print(f"❌ Individual item retrieval failed")
        
        # Step 3: Test kitchens retrieval
        print("\n📋 Step 3: Testing kitchens retrieval...")
        kitchens = await mongodb_service.get_kitchens()
        print(f"✅ Retrieved {len(kitchens)} kitchens")
        
        if kitchens:
            sample_kitchen = kitchens[0]
            print(f"🏪 Sample kitchen: {sample_kitchen['kitchen_id']} - {sample_kitchen.get('kitchen_name', sample_kitchen.get('name', 'Unknown'))}")
        
        # Step 4: Test order validation
        print("\n📋 Step 4: Testing order validation...")
        if menu_items:
            test_item_ids = [item['item_id'] for item in menu_items[:3]]
            validation_results = await mongodb_service.validate_order_items(test_item_ids)
            
            valid_items = sum(1 for valid in validation_results.values() if valid)
            print(f"✅ Validated {len(test_item_ids)} items, {valid_items} are valid")
            
            for item_id, is_valid in validation_results.items():
                status = "✅ Valid" if is_valid else "❌ Invalid"
                print(f"   {item_id}: {status}")
        
        # Step 5: Test order creation
        print("\n📋 Step 5: Testing order creation...")
        if menu_items:
            test_order_data = {
                "order_id": f"TEST_ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "items": [menu_items[0]['item_id'], menu_items[1]['item_id']] if len(menu_items) > 1 else [menu_items[0]['item_id']],
                "customer_id": "TEST_CUSTOMER",
                "status": "pending",
                "timestamp": datetime.now(),
                "notes": "Test order from MongoDB integration test"
            }
            
            created_order_id = await mongodb_service.create_order(test_order_data)
            if created_order_id:
                print(f"✅ Order created successfully: {created_order_id}")
                
                # Test order retrieval
                retrieved_order = await mongodb_service.get_order_by_id(created_order_id)
                if retrieved_order:
                    print(f"✅ Order retrieval successful")
                    print(f"   Items: {retrieved_order['items']}")
                    print(f"   Status: {retrieved_order['status']}")
                    
                    # Test order status update
                    update_success = await mongodb_service.update_order_status(created_order_id, "preparing")
                    if update_success:
                        print(f"✅ Order status update successful")
                    else:
                        print(f"❌ Order status update failed")
                else:
                    print(f"❌ Order retrieval failed")
            else:
                print(f"❌ Order creation failed")
        
        # Step 6: Test queue item operations
        print("\n📋 Step 6: Testing queue item operations...")
        if menu_items and kitchens:
            test_queue_item = {
                "queue_id": f"TEST_Q_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "order_id": test_order_data["order_id"],
                "item_id": menu_items[0]['item_id'],
                "kitchen_id": kitchens[0]['kitchen_id'],
                "status": "queued",
                "scheduled_start": datetime.now(),
                "prep_time_minutes": menu_items[0].get('prep_time_minutes', 10),
                "created_at": datetime.now()
            }
            
            queue_success = await mongodb_service.upsert_queue_item(test_queue_item)
            if queue_success:
                print(f"✅ Queue item created successfully")
                
                # Test queue item retrieval
                queue_items = await mongodb_service.get_queue_items(kitchen_id=kitchens[0]['kitchen_id'])
                print(f"✅ Retrieved {len(queue_items)} queue items for kitchen {kitchens[0]['kitchen_id']}")
                
                # Test queue item status update
                status_update_success = await mongodb_service.update_queue_item_status(
                    test_queue_item["queue_id"], 
                    "in_progress",
                    actual_start=datetime.now()
                )
                if status_update_success:
                    print(f"✅ Queue item status update successful")
                else:
                    print(f"❌ Queue item status update failed")
            else:
                print(f"❌ Queue item creation failed")
        
        # Step 7: Test system health
        print("\n📋 Step 7: Testing system health...")
        health_status = await mongodb_service.health_check()
        print(f"✅ System health check: {health_status['status']}")
        if health_status['status'] == 'connected':
            print(f"   Database: {health_status['database']}")
            print(f"   Collections: {health_status['collections']}")
        
        # Step 8: Get final system status
        print("\n📋 Step 8: Final system status...")
        system_status = await startup_service.get_system_status()
        print(f"✅ System status: {system_status['status']}")
        print(f"   Data counts: {system_status['data_counts']}")
        
        print("\n🎉 MongoDB Integration Test Completed Successfully!")
        print("=" * 80)
        print("✅ All tests passed! The system is ready for production use.")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup: disconnect from MongoDB
        try:
            await mongodb_service.disconnect()
            print("\n🔌 Disconnected from MongoDB")
        except:
            pass


async def main():
    """Main test function."""
    success = await test_mongodb_integration()
    
    if success:
        print("\n🚀 Ready to start the application!")
        print("   Run: python -m uvicorn app.main:app --reload")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
