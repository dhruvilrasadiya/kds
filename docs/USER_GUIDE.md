# Smart Kitchen Queue Management System - User Guide

## Overview

The Smart Kitchen Queue Management System is an AI-powered solution that optimizes food preparation across multiple kitchens, ensuring efficient order processing while preventing item starvation.

## Getting Started

### Accessing the System

1. **Web Interface**: Open your browser and navigate to `http://localhost:8000`
2. **API Documentation**: Visit `http://localhost:8000/docs` for interactive API documentation
3. **Health Check**: Check system status at `http://localhost:8000/api/system/health`

### System Components

#### Kitchens
The system manages three specialized kitchens:
- **Kitchen A (Grill Station)**: Handles grilled items (capacity: 3 items)
- **Kitchen B (Pasta Station)**: Manages pasta and rice dishes (capacity: 2 items)
- **Kitchen C (Dessert Station)**: Prepares desserts and beverages (capacity: 4 items)

#### Menu Items
Each item belongs to a specific kitchen and has:
- Preparation time estimate
- Difficulty level
- Availability status

## Core Features

### 1. Order Management

#### Creating Orders
Orders can contain multiple items from different kitchens. The AI system automatically:
- Validates item availability
- Assigns items to appropriate kitchens
- Optimizes preparation scheduling
- Ensures synchronized completion

**Example Order Flow:**
1. Customer selects items: Grilled Chicken, Spaghetti Bolognese, Chocolate Cake
2. System validates all items are available
3. AI optimizes scheduling across Kitchen A, B, and C
4. Items are queued with synchronized completion times
5. Order confirmation provided with estimated completion time

#### Order Status Tracking
- **Pending**: Order received, awaiting processing
- **Processing**: Items are being prepared
- **Completed**: All items finished
- **Cancelled**: Order was cancelled

### 2. Kitchen Operations

#### Queue Management
Each kitchen maintains a priority-based queue:
- **Emergency Priority**: Items experiencing starvation
- **High Priority**: Urgent or delayed items
- **Normal Priority**: Standard items
- **Low Priority**: Non-urgent items

#### Item Processing
Kitchen staff can:
- Start item preparation
- Mark items as completed
- View current queue status
- Check estimated completion times

### 3. AI-Driven Optimization

#### Intelligent Scheduling
The AI agent considers:
- Current kitchen loads and capacities
- Historical preparation times
- Item difficulty levels
- Synchronization requirements
- Anti-starvation mechanisms

#### Learning System
The system continuously learns from:
- Actual vs. estimated preparation times
- Kitchen efficiency patterns
- Peak load periods
- Bottleneck identification

### 4. Anti-Starvation Prevention

#### Starvation Detection
Items are considered "starving" when:
- Delayed 3 or more times
- Waiting longer than expected
- Consistently deprioritized

#### Emergency Interventions
When starvation is detected:
- Item receives emergency priority
- Immediate scheduling bypass
- Kitchen capacity override if necessary
- Real-time alerts generated

## Using the System

### For Kitchen Managers

#### Monitoring Kitchen Status
```
GET /api/kitchens/status
```
View all kitchen statuses including:
- Current load and capacity
- Queue contents
- Next available time slots
- Efficiency metrics

#### Managing Individual Kitchens
```
GET /api/kitchens/{kitchen_id}
```
Get detailed information for a specific kitchen:
- Current queue items
- Processing status
- Performance metrics

### For Kitchen Staff

#### Starting Item Preparation
```
PUT /api/kitchens/{kitchen_id}/start/{item_id}
```
Mark an item as started when beginning preparation.

#### Completing Items
```
PUT /api/kitchens/{kitchen_id}/complete/{item_id}
```
Mark an item as completed when finished.

### For Order Management

#### Creating New Orders
```
POST /api/orders/
{
  "items": ["ITM_001", "ITM_004", "ITM_007"],
  "customer_id": "CUST_001",
  "notes": "Special dietary requirements"
}
```

#### Tracking Order Progress
```
GET /api/orders/{order_id}
```
Monitor order status and estimated completion times.

#### Cancelling Orders
```
PUT /api/orders/{order_id}/cancel
```
Cancel orders before completion.

### For System Administrators

#### System Health Monitoring
```
GET /api/system/health
```
Check overall system health and component status.

#### Performance Analytics
```
GET /api/realtime/performance
```
View real-time performance metrics including:
- Kitchen utilization rates
- Average preparation times
- Starvation statistics
- Bottleneck identification

#### Configuration Management
```
POST /api/system/reload-config
```
Reload system configuration from Excel files.

## Real-Time Features

### Queue Status Updates
Monitor live queue status across all kitchens:
```
GET /api/realtime/queue
```

### Performance Metrics
Track system performance in real-time:
- Order completion rates
- Kitchen efficiency
- Starvation incidents
- Bottleneck alerts

### Emergency Controls
Trigger emergency actions when needed:
```
POST /api/realtime/emergency-reschedule
```

## Configuration

### Excel-Based Configuration
The system uses Excel files for configuration:

#### Kitchen Configuration (`kitchens` sheet)
- Kitchen IDs and names
- Capacity settings
- Specializations
- Status (active/inactive)

#### Menu Items (`items` sheet)
- Item IDs and names
- Kitchen assignments
- Preparation times
- Difficulty levels
- Availability status

#### Historical Data (`historical_performance` sheet)
- Past performance records
- Actual vs. scheduled times
- Kitchen load data
- Learning data for AI

#### Load Patterns (`kitchen_load_patterns` sheet)
- Hourly load patterns
- Seasonal variations
- Capacity planning data

### Environment Configuration
Key settings in `.env` file:
- `MAX_STARVATION_COUNT`: Delay threshold for starvation (default: 3)
- `SYNCHRONIZATION_WINDOW_MINUTES`: Time window for order synchronization (default: 3)
- `PERFORMANCE_HISTORY_DAYS`: Days of historical data to retain (default: 30)

## Best Practices

### For Optimal Performance

1. **Regular Monitoring**: Check system health and performance metrics daily
2. **Configuration Updates**: Keep menu items and kitchen settings current
3. **Staff Training**: Ensure kitchen staff understand the priority system
4. **Data Maintenance**: Regularly review and clean historical data

### For Kitchen Efficiency

1. **Capacity Management**: Don't exceed kitchen capacities
2. **Priority Respect**: Process emergency items immediately
3. **Accurate Timing**: Update actual completion times for learning
4. **Communication**: Use order notes for special requirements

### For System Administration

1. **Backup Configuration**: Regular backups of Excel configuration files
2. **Log Monitoring**: Review system logs for errors and warnings
3. **Performance Tuning**: Adjust settings based on usage patterns
4. **Security Updates**: Keep system dependencies updated

## Troubleshooting

### Common Issues

#### High Starvation Rates
**Symptoms**: Many items showing emergency priority
**Solutions**:
- Review kitchen capacities
- Check for bottlenecks
- Adjust starvation threshold
- Balance kitchen loads

#### Slow Response Times
**Symptoms**: API calls taking too long
**Solutions**:
- Check AI service status
- Review system resources
- Clear old historical data
- Restart services if needed

#### Synchronization Problems
**Symptoms**: Order items completing at different times
**Solutions**:
- Adjust synchronization window
- Review preparation time estimates
- Check kitchen efficiency
- Reoptimize pending orders

### Getting Help

1. **System Health**: Check `/api/system/health` for component status
2. **Logs**: Review application logs in `logs/kitchen_queue.log`
3. **Metrics**: Use performance metrics to identify issues
4. **Documentation**: Refer to API documentation for usage details

## Advanced Features

### Custom AI Prompts
The system allows customization of AI decision-making prompts for specific business needs.

### Integration APIs
RESTful APIs enable integration with:
- POS systems
- Inventory management
- Customer notification systems
- Analytics platforms

### Reporting
Generate comprehensive reports on:
- Kitchen performance
- Order completion rates
- Efficiency trends
- Starvation incidents

This user guide provides comprehensive information for all system users, from kitchen staff to system administrators.
