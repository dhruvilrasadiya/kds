#!/usr/bin/env python3
"""
Test script to verify API endpoints with MongoDB integration.
This script tests the complete API flow with MongoDB backend.
"""

import requests
import json
import time
from datetime import datetime


def test_api_endpoints():
    """Test all API endpoints with MongoDB backend."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API Endpoints with MongoDB Integration")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n📋 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Get menu items
    print("\n📋 Test 2: Get Menu Items")
    try:
        response = requests.get(f"{base_url}/api/menu/items")
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ Retrieved {len(items)} menu items")
            
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


def test_order_creation(menu_items):
    """Test order creation with MongoDB."""
    base_url = "http://localhost:8000"
    
    if not menu_items:
        print("⚠️ No menu items available for order test")
        return None
    
    print("\n📋 Test 3: Create Order")
    try:
        # Create test order
        order_data = {
            "items": [menu_items[0]["item_id"]],
            "customer_id": "TEST_CUSTOMER_API",
            "notes": "Test order via API with MongoDB"
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


def test_order_retrieval(order_id):
    """Test order retrieval from MongoDB."""
    base_url = "http://localhost:8000"
    
    if not order_id:
        return
    
    print("\n📋 Test 4: Get Order")
    try:
        response = requests.get(f"{base_url}/api/orders/{order_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                order = data["order"]
                print(f"✅ Order retrieved successfully: {order['order_id']}")
                print(f"   Status: {order['status']}")
                print(f"   Items: {order['items']}")
            else:
                print(f"❌ Order retrieval failed: {data.get('message')}")
        else:
            print(f"❌ Order retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Order retrieval error: {e}")


def test_orders_list():
    """Test orders listing from MongoDB."""
    base_url = "http://localhost:8000"
    
    print("\n📋 Test 5: List Orders")
    try:
        response = requests.get(f"{base_url}/api/orders/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                orders = data.get("orders", [])
                print(f"✅ Retrieved {len(orders)} orders")
                print(f"   Total count: {data.get('total_count', 0)}")
            else:
                print(f"❌ Orders list failed: {data.get('message')}")
        else:
            print(f"❌ Orders list failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Orders list error: {e}")


def test_kitchens():
    """Test kitchens API with MongoDB."""
    base_url = "http://localhost:8000"
    
    print("\n📋 Test 6: Get Kitchens")
    try:
        response = requests.get(f"{base_url}/api/kitchens/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                kitchens = data.get("kitchens", [])
                print(f"✅ Retrieved {len(kitchens)} kitchens")
                
                if kitchens:
                    sample_kitchen = kitchens[0]
                    print(f"   Sample: {sample_kitchen.get('kitchen_id')} - {sample_kitchen.get('name', sample_kitchen.get('kitchen_name'))}")
            else:
                print(f"❌ Kitchens failed: {data.get('message')}")
        else:
            print(f"❌ Kitchens failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Kitchens error: {e}")


def test_system_health():
    """Test system health with MongoDB."""
    base_url = "http://localhost:8000"
    
    print("\n📋 Test 7: System Health")
    try:
        response = requests.get(f"{base_url}/api/system/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System health check passed")
            print(f"   Status: {data.get('status', 'unknown')}")
            
            # Check MongoDB status if available
            mongodb_status = data.get('mongodb', {})
            if mongodb_status:
                print(f"   MongoDB: {mongodb_status.get('status', 'unknown')}")
        else:
            print(f"❌ System health failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ System health error: {e}")


def main():
    """Main test function."""
    print("🚀 Starting API Tests with MongoDB Integration")
    print("Make sure the server is running: python -m uvicorn app.main:app --reload")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Run tests
    menu_items = test_api_endpoints()
    order_id = test_order_creation(menu_items)
    test_order_retrieval(order_id)
    test_orders_list()
    test_kitchens()
    test_system_health()
    
    print("\n🎉 API Testing Completed!")
    print("=" * 60)
    
    if menu_items and order_id:
        print("✅ All major tests passed! MongoDB integration is working.")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")


if __name__ == "__main__":
    main()
