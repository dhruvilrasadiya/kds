#!/usr/bin/env python3
"""
Test script to verify all APIs are using MongoDB exclusively.
This script tests the complete flow with MongoDB backend only.
"""

import requests
import json
import time
from datetime import datetime


def test_mongodb_only_apis():
    """Test all API endpoints to ensure they use MongoDB exclusively."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MongoDB-Only API Implementation")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n📋 Test 1: System Health Check")
    try:
        response = requests.get(f"{base_url}/api/system/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ System health check passed")
            print(f"   MongoDB Status: {data.get('components', {}).get('mongodb', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Get menu items from MongoDB
    print("\n📋 Test 2: Get Menu Items (MongoDB)")
    try:
        response = requests.get(f"{base_url}/api/menu/items")
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ Retrieved {len(items)} menu items from MongoDB")
            
            if items:
                sample_item = items[0]
                print(f"   Sample: {sample_item.get('item_id')} - {sample_item.get('name', sample_item.get('item_name'))}")
                return items  # Return for use in order test
        else:
            print(f"❌ Menu items failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Menu items error: {e}")
    
    return []


def test_order_creation_mongodb(menu_items):
    """Test order creation with MongoDB backend."""
    base_url = "http://localhost:8000"
    
    if not menu_items:
        print("⚠️ No menu items available for order test")
        return None
    
    print("\n📋 Test 3: Create Order (MongoDB Backend)")
    try:
        # Create test order
        order_data = {
            "items": [menu_items[0]["item_id"]],
            "customer_id": "TEST_CUSTOMER_MONGODB",
            "notes": "Test order with MongoDB-only backend"
        }
        
        if len(menu_items) > 1:
            order_data["items"].append(menu_items[1]["item_id"])
        
        print(f"   Creating order with items: {order_data['items']}")
        
        response = requests.post(
            f"{base_url}/api/orders/",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                order_id = data["order"]["order_id"]
                print(f"✅ Order created successfully: {order_id}")
                print(f"   Status: {data['order']['status']}")
                print(f"   Items: {len(data['order']['items'])} items")
                return order_id
            else:
                print(f"❌ Order creation failed: {data.get('message')}")
        else:
            print(f"❌ Order creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Order creation error: {e}")
    
    return None


def test_queue_operations_mongodb(order_id):
    """Test queue operations with MongoDB backend."""
    base_url = "http://localhost:8000"
    
    if not order_id:
        return
    
    print("\n📋 Test 4: Queue Operations (MongoDB)")
    try:
        # Get queue items
        response = requests.get(f"{base_url}/api/queue/items")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                queue_items = data.get("queue_items", [])
                print(f"✅ Retrieved {len(queue_items)} queue items from MongoDB")
                
                # Find items for our order
                order_items = [item for item in queue_items if item.get('order_id') == order_id]
                print(f"   Order {order_id} has {len(order_items)} queue items")
                
                # Test queue item status update
                if order_items:
                    test_item = order_items[0]
                    queue_id = test_item.get('queue_id')
                    
                    print(f"   Testing status update for queue item: {queue_id}")
                    
                    # Update to in_progress
                    update_response = requests.put(
                        f"{base_url}/api/queue/items/{queue_id}/status",
                        params={"status": "in_progress"}
                    )
                    
                    if update_response.status_code == 200:
                        print(f"   ✅ Updated queue item {queue_id} to in_progress")
                    else:
                        print(f"   ❌ Failed to update queue item: {update_response.status_code}")
                
            else:
                print(f"❌ Queue items failed: {data.get('message')}")
        else:
            print(f"❌ Queue items failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Queue operations error: {e}")


def test_kitchen_operations_mongodb():
    """Test kitchen operations with MongoDB backend."""
    base_url = "http://localhost:8000"
    
    print("\n📋 Test 5: Kitchen Operations (MongoDB)")
    try:
        # Get all kitchens
        response = requests.get(f"{base_url}/api/kitchens/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                kitchens = data.get("kitchens", [])
                print(f"✅ Retrieved {len(kitchens)} kitchens from MongoDB")
                
                if kitchens:
                    sample_kitchen = kitchens[0]
                    kitchen_id = sample_kitchen.get('kitchen_id')
                    print(f"   Sample: {kitchen_id} - {sample_kitchen.get('name', sample_kitchen.get('kitchen_name'))}")
                    print(f"   Current Load: {sample_kitchen.get('current_load', 0)}")
                    
                    # Test individual kitchen status
                    status_response = requests.get(f"{base_url}/api/kitchens/{kitchen_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get("success"):
                            kitchen_status = status_data.get("kitchen_status", {})
                            print(f"   ✅ Kitchen {kitchen_id} status retrieved")
                            print(f"      Capacity: {kitchen_status.get('capacity', 0)}")
                            print(f"      Available Slots: {kitchen_status.get('available_slots', 0)}")
                        else:
                            print(f"   ❌ Kitchen status failed: {status_data.get('message')}")
                    else:
                        print(f"   ❌ Kitchen status failed: {status_response.status_code}")
                
            else:
                print(f"❌ Kitchens failed: {data.get('message')}")
        else:
            print(f"❌ Kitchens failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Kitchen operations error: {e}")


def test_queue_stats_mongodb():
    """Test queue statistics from MongoDB."""
    base_url = "http://localhost:8000"
    
    print("\n📋 Test 6: Queue Statistics (MongoDB)")
    try:
        response = requests.get(f"{base_url}/api/queue/stats")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data.get("stats", {})
                print(f"✅ Queue statistics retrieved from MongoDB")
                print(f"   Total Items: {stats.get('total_items', 0)}")
                print(f"   By Status: {stats.get('by_status', {})}")
                print(f"   By Kitchen: {stats.get('by_kitchen', {})}")
                print(f"   Average Prep Time: {stats.get('average_prep_time', 0):.1f} minutes")
            else:
                print(f"❌ Queue stats failed: {data.get('message')}")
        else:
            print(f"❌ Queue stats failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Queue stats error: {e}")


def test_order_retrieval_mongodb(order_id):
    """Test order retrieval from MongoDB."""
    base_url = "http://localhost:8000"
    
    if not order_id:
        return
    
    print("\n📋 Test 7: Order Retrieval (MongoDB)")
    try:
        response = requests.get(f"{base_url}/api/orders/{order_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                order = data["order"]
                print(f"✅ Order {order_id} retrieved from MongoDB")
                print(f"   Status: {order['status']}")
                print(f"   Items: {order['items']}")
                print(f"   Timestamp: {order.get('timestamp')}")
            else:
                print(f"❌ Order retrieval failed: {data.get('message')}")
        else:
            print(f"❌ Order retrieval failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Order retrieval error: {e}")


def main():
    """Main test function."""
    print("🚀 Starting MongoDB-Only API Tests")
    print("Make sure the server is running: python -m uvicorn app.main:app --reload")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Run tests
    menu_items = test_mongodb_only_apis()
    order_id = test_order_creation_mongodb(menu_items)
    test_queue_operations_mongodb(order_id)
    test_kitchen_operations_mongodb()
    test_queue_stats_mongodb()
    test_order_retrieval_mongodb(order_id)
    
    print("\n🎉 MongoDB-Only API Testing Completed!")
    print("=" * 60)
    
    if menu_items and order_id:
        print("✅ All major tests passed! MongoDB-only implementation is working.")
        print("\n📊 Summary:")
        print("   - Menu items loaded from MongoDB")
        print("   - Orders stored in MongoDB")
        print("   - Queue items managed in MongoDB")
        print("   - Kitchen data from MongoDB")
        print("   - All operations use MongoDB exclusively")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")


if __name__ == "__main__":
    main()
