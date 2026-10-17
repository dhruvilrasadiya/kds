# Smart Kitchen Queue Management System - API Documentation

## Overview

The Smart Kitchen Queue Management System provides a comprehensive REST API for managing kitchen operations, order processing, and real-time monitoring with AI-driven optimization.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement appropriate authentication mechanisms.

## API Endpoints

### Orders Management

#### Create Order
- **POST** `/api/orders/`
- **Description**: Create a new order with AI-optimized scheduling
- **Request Body**:
```json
{
  "items": ["ITM_001", "ITM_004", "ITM_007"],
  "customer_id": "CUST_001",
  "notes": "Special instructions"
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Order ORD_12345678 created successfully",
  "order": {
    "order_id": "ORD_12345678",
    "items": ["ITM_001", "ITM_004", "ITM_007"],
    "status": "processing",
    "estimated_completion": "2024-01-01T12:30:00Z",
    "total_prep_time": 45
  }
}
```

#### Get Order
- **GET** `/api/orders/{order_id}`
- **Description**: Retrieve order details and current status
- **Response**: Order object with current status and queue items

#### List Orders
- **GET** `/api/orders/`
- **Query Parameters**:
  - `status`: Filter by order status (pending, processing, completed, cancelled)
  - `limit`: Number of orders to return (default: 50)
  - `offset`: Pagination offset (default: 0)

#### Cancel Order
- **PUT** `/api/orders/{order_id}/cancel`
- **Description**: Cancel an existing order

### Kitchen Management

#### Get All Kitchen Statuses
- **GET** `/api/kitchens/status`
- **Description**: Get current status of all kitchens
- **Response**:
```json
{
  "success": true,
  "kitchen_statuses": [
    {
      "kitchen_id": "KITCHEN_A",
      "kitchen_name": "Grill Station",
      "capacity": 3,
      "current_load": 2,
      "available_slots": 1,
      "current_queue": [...],
      "next_available_time": "2024-01-01T12:15:00Z"
    }
  ]
}
```

#### Get Kitchen Status
- **GET** `/api/kitchens/{kitchen_id}`
- **Description**: Get detailed status for a specific kitchen

#### Complete Item
- **PUT** `/api/kitchens/{kitchen_id}/complete/{item_id}`
- **Description**: Mark an item as completed
- **Request Body**:
```json
{
  "actual_completion_time": "2024-01-01T12:20:00Z",
  "notes": "Completed successfully"
}
```

#### Start Item
- **PUT** `/api/kitchens/{kitchen_id}/start/{item_id}`
- **Description**: Mark an item as started

#### Get Kitchen Efficiency
- **GET** `/api/kitchens/{kitchen_id}/efficiency`
- **Query Parameters**:
  - `days`: Number of days to analyze (default: 7)

### Real-time Operations

#### Get Queue Status
- **GET** `/api/realtime/queue`
- **Description**: Get current queue status across all kitchens

#### Get Performance Metrics
- **GET** `/api/realtime/performance`
- **Description**: Get real-time system performance metrics

#### Get Performance History
- **POST** `/api/realtime/performance/history`
- **Description**: Query historical performance data
- **Request Body**:
```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-02T00:00:00Z",
  "kitchen_id": "KITCHEN_A",
  "limit": 100
}
```

#### Get Starvation Status
- **GET** `/api/realtime/starvation`
- **Description**: Get current starvation status and statistics

#### Trigger Reoptimization
- **POST** `/api/realtime/reoptimize`
- **Description**: Manually trigger AI reoptimization of pending orders

#### Emergency Reschedule
- **POST** `/api/realtime/emergency-reschedule`
- **Description**: Trigger emergency rescheduling for starving items

### System Management

#### Health Check
- **GET** `/api/system/health`
- **Description**: Comprehensive system health check
- **Response**:
```json
{
  "success": true,
  "status": "healthy",
  "components": {
    "excel_service": "healthy - 3 kitchens loaded",
    "queue_manager": "healthy - 5 items in queues",
    "ai_agent": "healthy - agent initialized"
  },
  "uptime": "2:30:45",
  "version": "1.0.0"
}
```

#### Reload Configuration
- **POST** `/api/system/reload-config`
- **Description**: Reload system configuration from Excel files
- **Request Body**:
```json
{
  "force_reload": true,
  "clear_cache": true
}
```

#### Get System Metrics
- **GET** `/api/system/metrics`
- **Description**: Get comprehensive system metrics

#### Get Learning Report
- **GET** `/api/system/learning-report`
- **Description**: Get AI learning and performance report

#### Get Current Configuration
- **GET** `/api/system/config`
- **Description**: Get current system configuration

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common HTTP Status Codes

- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Resource Not Found
- `500`: Internal Server Error

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting for production use.

## WebSocket Support

Real-time updates can be implemented using WebSocket connections for live queue status updates.

## Data Models

### Order
```json
{
  "order_id": "string",
  "items": ["string"],
  "timestamp": "datetime",
  "status": "pending|processing|completed|cancelled",
  "estimated_completion": "datetime",
  "actual_completion": "datetime",
  "total_prep_time": "integer"
}
```

### QueueItem
```json
{
  "item_id": "string",
  "item_name": "string",
  "order_id": "string",
  "prep_time": "integer",
  "scheduled_start": "datetime",
  "estimated_completion": "datetime",
  "priority_level": "low|normal|high|emergency",
  "starvation_count": "integer",
  "status": "queued|in_progress|completed|cancelled",
  "kitchen_id": "string"
}
```

### KitchenStatus
```json
{
  "kitchen_id": "string",
  "kitchen_name": "string",
  "capacity": "integer",
  "current_load": "integer",
  "available_slots": "integer",
  "current_queue": ["QueueItem"],
  "next_available_time": "datetime",
  "status": "active|inactive|maintenance"
}
```
