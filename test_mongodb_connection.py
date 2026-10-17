#!/usr/bin/env python3
"""
Test MongoDB Connection Script
=============================

This script tests different MongoDB connection configurations to help
identify the correct connection string for your setup.
"""

import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

def test_connection(url, description):
    """Test a MongoDB connection URL."""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    
    try:
        client = MongoClient(url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("   ✅ Connection successful!")
        
        # Test database access
        db = client.smart_kitchen
        
        # Try to list collections (this requires read permissions)
        collections = db.list_collection_names()
        print(f"   ✅ Database access successful! Found {len(collections)} collections")
        
        # Try to create a test document (this requires write permissions)
        test_collection = db.connection_test
        result = test_collection.insert_one({"test": "connection", "timestamp": "now"})
        print(f"   ✅ Write access successful! Document ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("   ✅ Cleanup successful!")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    except OperationFailure as e:
        print(f"   ❌ Operation failed (likely authentication): {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    """Test various MongoDB connection configurations."""
    print("🧪 MongoDB Connection Tester")
    print("=" * 50)
    
    # Test configurations
    test_configs = [
        {
            "url": "mongodb://127.0.0.1:27017",
            "description": "Local MongoDB without authentication"
        },
        {
            "url": "mongodb://admin:password123@127.0.0.1:27017/smart_kitchen?authSource=admin",
            "description": "Local MongoDB with admin credentials (Docker default)"
        },
        {
            "url": "mongodb://127.0.0.1:27017/smart_kitchen",
            "description": "Local MongoDB with database specified"
        },
        {
            "url": "mongodb://localhost:27017",
            "description": "Local MongoDB using localhost"
        },
        {
            "url": "mongodb://admin:password123@localhost:27017/smart_kitchen?authSource=admin",
            "description": "Local MongoDB with admin credentials using localhost"
        }
    ]
    
    successful_connections = []
    
    for config in test_configs:
        if test_connection(config["url"], config["description"]):
            successful_connections.append(config)
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    
    if successful_connections:
        print(f"✅ Found {len(successful_connections)} working connection(s):")
        for i, config in enumerate(successful_connections, 1):
            print(f"\n{i}. {config['description']}")
            print(f"   URL: {config['url']}")
        
        print(f"\n🎯 RECOMMENDED: Use this connection string:")
        print(f"   {successful_connections[0]['url']}")
        
        print(f"\n📋 To use with migration script:")
        print(f"   python excel_to_mongodb_sync.py --mongodb-url \"{successful_connections[0]['url']}\"")
        
    else:
        print("❌ No successful connections found!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure MongoDB is running:")
        print("   - Docker: docker-compose up -d mongodb")
        print("   - Local: sudo systemctl start mongod")
        print("2. Check if MongoDB is listening on port 27017:")
        print("   - netstat -tulpn | grep 27017")
        print("3. Verify MongoDB credentials if authentication is enabled")
        print("4. Check MongoDB logs for error messages")
        
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
