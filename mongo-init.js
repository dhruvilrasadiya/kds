// MongoDB initialization script for Smart Kitchen Queue Management System

// Switch to the smart_kitchen database
db = db.getSiblingDB('smart_kitchen');

// Create collections with validation schemas
db.createCollection('menu_items', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['item_id', 'item_name', 'kitchen_id', 'prep_time_minutes'],
      properties: {
        item_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        item_name: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        kitchen_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        prep_time_minutes: {
          bsonType: 'int',
          minimum: 1,
          description: 'must be an integer greater than 0 and is required'
        },
        available: {
          bsonType: 'bool',
          description: 'must be a boolean'
        },
        price: {
          bsonType: 'double',
          minimum: 0,
          description: 'must be a positive number'
        }
      }
    }
  }
});

db.createCollection('kitchens', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['kitchen_id', 'name', 'capacity'],
      properties: {
        kitchen_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        name: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        capacity: {
          bsonType: 'int',
          minimum: 1,
          description: 'must be an integer greater than 0 and is required'
        },
        status: {
          bsonType: 'string',
          enum: ['active', 'inactive', 'maintenance'],
          description: 'must be one of the enum values'
        }
      }
    }
  }
});

db.createCollection('orders', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['order_id', 'items', 'status', 'timestamp'],
      properties: {
        order_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        items: {
          bsonType: 'array',
          description: 'must be an array and is required'
        },
        status: {
          bsonType: 'string',
          enum: ['cooking', 'preparing', 'ready', 'on-hold'],
          description: 'must be one of the enum values and is required'
        },
        timestamp: {
          bsonType: 'date',
          description: 'must be a date and is required'
        }
      }
    }
  }
});

db.createCollection('queue_items', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['queue_id', 'item_id', 'order_id', 'kitchen_id', 'status'],
      properties: {
        queue_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        item_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        order_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        kitchen_id: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        status: {
          bsonType: 'string',
          enum: ['queued', 'in_progress', 'completed', 'cancelled'],
          description: 'must be one of the enum values and is required'
        }
      }
    }
  }
});

// Create indexes for better performance
db.menu_items.createIndex({ 'item_id': 1 }, { unique: true });
db.menu_items.createIndex({ 'category': 1 });
db.menu_items.createIndex({ 'available': 1 });

db.kitchens.createIndex({ 'kitchen_id': 1 }, { unique: true });
db.kitchens.createIndex({ 'status': 1 });

db.orders.createIndex({ 'order_id': 1 }, { unique: true });
db.orders.createIndex({ 'status': 1 });
db.orders.createIndex({ 'timestamp': -1 });

db.queue_items.createIndex({ 'queue_id': 1 }, { unique: true });
db.queue_items.createIndex({ 'order_id': 1 });
db.queue_items.createIndex({ 'kitchen_id': 1 });
db.queue_items.createIndex({ 'status': 1 });

print('MongoDB initialization completed successfully!');
print('Collections created: menu_items, kitchens, orders, queue_items');
print('Indexes created for optimal performance');
