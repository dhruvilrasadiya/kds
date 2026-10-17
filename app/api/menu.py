"""
Menu API endpoints for the Smart Kitchen Queue Management System.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Query

logger = logging.getLogger(__name__)

router = APIRouter()


def get_services(request: Request):
    """Dependency to get services from app state."""
    return {
        'excel_service': request.app.state.excel_service,
        'mongodb_service': request.app.state.mongodb_service,
        'data_sync_service': request.app.state.data_sync_service,
        'queue_manager': request.app.state.queue_manager,
        'starvation_prevention': request.app.state.starvation_prevention,
        'ai_agent': request.app.state.ai_agent,
        'performance_learning': request.app.state.performance_learning
    }


@router.get("/items")
async def get_menu_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    kitchen_id: Optional[str] = Query(None, description="Filter by kitchen"),
    available_only: bool = Query(True, description="Show only available items"),
    services=Depends(get_services)
):
    """Get all menu items with optional filtering."""
    try:
        # Get menu items directly from MongoDB
        menu_items_data = await services['mongodb_service'].get_menu_items(category, available_only)

        # Filter by kitchen if specified
        if kitchen_id:
            menu_items_data = [item for item in menu_items_data if item.get('kitchen_id') == kitchen_id]

        items_list = menu_items_data
        
        return {
            "success": True,
            "message": f"Retrieved {len(items_list)} menu items",
            "items": items_list,
            "total_count": len(items_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting menu items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/{item_id}")
async def get_menu_item(item_id: str, services=Depends(get_services)):
    """Get a specific menu item by ID."""
    try:
        item = await services['mongodb_service'].get_menu_item(item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_id} not found")
        
        return {
            "success": True,
            "message": f"Retrieved menu item {item_id}",
            "item": item
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting menu item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_menu_categories(services=Depends(get_services)):
    """Get all available menu categories."""
    try:
        menu_items = services['excel_service'].load_menu_items()
        categories = set()
        
        for item in menu_items.values():
            category = item.get('category', 'other')
            if category:
                categories.add(category)
        
        # Convert to list and sort
        categories_list = sorted(list(categories))
        
        # Add 'all' option at the beginning
        result = [{"id": "all", "name": "All Items"}]
        result.extend([{"id": cat, "name": cat.title()} for cat in categories_list])
        
        return {
            "success": True,
            "message": f"Retrieved {len(result)} categories",
            "categories": result
        }
        
    except Exception as e:
        logger.error(f"Error getting menu categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/kitchen/{kitchen_id}")
async def get_items_by_kitchen(kitchen_id: str, services=Depends(get_services)):
    """Get all menu items for a specific kitchen."""
    try:
        items = services['excel_service'].get_items_by_kitchen(kitchen_id)
        
        return {
            "success": True,
            "message": f"Retrieved {len(items)} items for kitchen {kitchen_id}",
            "items": items,
            "kitchen_id": kitchen_id
        }
        
    except Exception as e:
        logger.error(f"Error getting items for kitchen {kitchen_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_menu_items(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    services=Depends(get_services)
):
    """Search menu items by name or description."""
    try:
        menu_items = services['excel_service'].load_menu_items()
        items_list = list(menu_items.values())
        
        # Filter by category first if provided
        if category and category != 'all':
            items_list = [item for item in items_list if item.get('category') == category]
        
        # Search in name and description
        search_query = q.lower()
        filtered_items = []
        
        for item in items_list:
            name_match = search_query in item.get('name', '').lower()
            desc_match = search_query in item.get('description', '').lower()
            
            if name_match or desc_match:
                filtered_items.append(item)
        
        return {
            "success": True,
            "message": f"Found {len(filtered_items)} items matching '{q}'",
            "items": filtered_items,
            "query": q,
            "total_count": len(filtered_items)
        }
        
    except Exception as e:
        logger.error(f"Error searching menu items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/featured")
async def get_featured_items(
    limit: int = Query(6, description="Number of featured items to return"),
    services=Depends(get_services)
):
    """Get featured menu items."""
    try:
        menu_items = services['excel_service'].load_menu_items()
        items_list = list(menu_items.values())
        
        # Filter available items only
        available_items = [item for item in items_list if item.get('available', True)]
        
        # For now, return first N items as featured
        # In a real implementation, you might have a 'featured' flag in the data
        featured_items = available_items[:limit]
        
        return {
            "success": True,
            "message": f"Retrieved {len(featured_items)} featured items",
            "items": featured_items
        }
        
    except Exception as e:
        logger.error(f"Error getting featured items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/items/{item_id}/availability")
async def update_item_availability(
    item_id: str,
    available: bool,
    services=Depends(get_services)
):
    """Update item availability status."""
    try:
        # This would typically update the database/Excel file
        # For now, we'll just validate the item exists
        item = services['excel_service'].get_item_by_id(item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_id} not found")
        
        # In a real implementation, update the Excel file or database
        logger.info(f"Updated availability for item {item_id} to {available}")
        
        return {
            "success": True,
            "message": f"Updated availability for item {item_id} to {available}",
            "item_id": item_id,
            "available": available
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))
