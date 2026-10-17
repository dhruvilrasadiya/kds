"""
API tests for the Smart Kitchen Queue Management System.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from app.main import app
from app.models import CreateOrderRequest, OrderStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock all services for API testing."""
    with patch('app.main.excel_service') as mock_excel, \
         patch('app.main.queue_manager') as mock_queue, \
         patch('app.main.starvation_prevention') as mock_starvation, \
         patch('app.main.ai_agent') as mock_ai, \
         patch('app.main.performance_learning') as mock_perf:
        
        # Setup mock returns
        mock_excel.validate_order_items.return_value = True
        mock_excel.load_kitchen_config.return_value = {
            "KITCHEN_A": {"kitchen_name": "Grill Station", "capacity": 3}
        }
        
        mock_queue.get_all_kitchen_statuses.return_value = []
        mock_queue.add_item_to_queue.return_value = True
        
        mock_ai.optimize_order_schedule.return_value = Mock(
            order_id="TEST_ORDER",
            optimized_items=[],
            total_estimated_time=30,
            synchronization_achieved=True,
            anti_starvation_applied=[],
            optimization_notes="Test optimization"
        )
        
        yield {
            'excel': mock_excel,
            'queue': mock_queue,
            'starvation': mock_starvation,
            'ai': mock_ai,
            'performance': mock_perf
        }


class TestOrdersAPI:
    """Test cases for Orders API."""
    
    def test_create_order_success(self, client, mock_services):
        """Test successful order creation."""
        order_data = {
            "items": ["ITM_001", "ITM_004"],
            "customer_id": "CUST_001",
            "notes": "Test order"
        }
        
        response = client.post("/api/orders/", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "order" in data
        assert data["order"]["items"] == order_data["items"]
    
    def test_create_order_invalid_items(self, client, mock_services):
        """Test order creation with invalid items."""
        mock_services['excel'].validate_order_items.return_value = False
        
        order_data = {
            "items": ["INVALID_ITEM"],
            "customer_id": "CUST_001"
        }
        
        response = client.post("/api/orders/", json=order_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
    
    def test_get_order_not_found(self, client, mock_services):
        """Test getting non-existent order."""
        response = client.get("/api/orders/NON_EXISTENT")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_list_orders(self, client, mock_services):
        """Test listing orders."""
        response = client.get("/api/orders/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "orders" in data
        assert "total_count" in data
    
    def test_cancel_order(self, client, mock_services):
        """Test cancelling order."""
        # First create an order
        order_data = {"items": ["ITM_001"]}
        create_response = client.post("/api/orders/", json=order_data)
        order_id = create_response.json()["order"]["order_id"]
        
        # Then cancel it
        response = client.put(f"/api/orders/{order_id}/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestKitchensAPI:
    """Test cases for Kitchens API."""
    
    def test_get_all_kitchen_statuses(self, client, mock_services):
        """Test getting all kitchen statuses."""
        response = client.get("/api/kitchens/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "kitchen_statuses" in data
    
    def test_get_kitchen_status(self, client, mock_services):
        """Test getting specific kitchen status."""
        mock_services['queue'].get_kitchen_status.return_value = Mock(
            kitchen_id="KITCHEN_A",
            kitchen_name="Grill Station",
            capacity=3,
            current_load=1
        )
        
        response = client.get("/api/kitchens/KITCHEN_A")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "kitchen_status" in data
    
    def test_get_kitchen_status_not_found(self, client, mock_services):
        """Test getting non-existent kitchen status."""
        mock_services['queue'].get_kitchen_status.return_value = None
        
        response = client.get("/api/kitchens/NON_EXISTENT")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_complete_item(self, client, mock_services):
        """Test completing an item."""
        mock_services['queue'].get_kitchen_status.return_value = Mock(
            current_queue=[Mock(item_id="ITM_001", order_id="ORD_001", prep_time=15)],
            current_load=1
        )
        mock_services['queue'].remove_completed_item.return_value = True
        
        completion_data = {"notes": "Completed successfully"}
        
        response = client.put("/api/kitchens/KITCHEN_A/complete/ITM_001", json=completion_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_start_item(self, client, mock_services):
        """Test starting an item."""
        mock_services['queue'].update_item_status.return_value = True
        
        response = client.put("/api/kitchens/KITCHEN_A/start/ITM_001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_kitchen_efficiency(self, client, mock_services):
        """Test getting kitchen efficiency."""
        mock_services['performance'].analyze_kitchen_efficiency.return_value = {
            "efficiency_metrics": {"avg_prep_time": 15.5}
        }
        
        response = client.get("/api/kitchens/KITCHEN_A/efficiency?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data


class TestRealtimeAPI:
    """Test cases for Real-time API."""
    
    def test_get_queue_status(self, client, mock_services):
        """Test getting queue status."""
        response = client.get("/api/realtime/queue")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "queue_items" in data
        assert "kitchen_loads" in data
    
    def test_get_performance_metrics(self, client, mock_services):
        """Test getting performance metrics."""
        mock_services['starvation'].get_starvation_statistics.return_value = {
            "currently_starving": 0
        }
        mock_services['performance'].identify_bottlenecks.return_value = []
        
        response = client.get("/api/realtime/performance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data
    
    def test_get_performance_history(self, client, mock_services):
        """Test getting performance history."""
        mock_services['excel'].load_historical_data.return_value = Mock(
            head=Mock(return_value=Mock(iterrows=Mock(return_value=[])))
        )
        
        query_data = {
            "start_date": "2024-01-01T00:00:00",
            "limit": 10
        }
        
        response = client.post("/api/realtime/performance/history", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "records" in data
    
    def test_get_starvation_status(self, client, mock_services):
        """Test getting starvation status."""
        mock_services['starvation'].get_starvation_statistics.return_value = {
            "currently_starving": 1
        }
        mock_services['starvation'].get_starving_items.return_value = ["ITM_001"]
        mock_services['starvation'].get_item_delay_info.return_value = {
            "item_id": "ITM_001",
            "delay_count": 3
        }
        
        response = client.get("/api/realtime/starvation")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "statistics" in data
        assert "starving_items_details" in data
    
    def test_trigger_reoptimization(self, client, mock_services):
        """Test triggering reoptimization."""
        mock_services['ai'].reoptimize_pending_orders.return_value = []
        
        response = client.post("/api/realtime/reoptimize")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reoptimization_results" in data
    
    def test_emergency_reschedule(self, client, mock_services):
        """Test emergency rescheduling."""
        mock_services['starvation'].get_starving_items.return_value = ["ITM_001"]
        mock_services['ai'].emergency_reschedule.return_value = {"status": "completed"}
        
        response = client.post("/api/realtime/emergency-reschedule")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "emergency_result" in data


class TestSystemAPI:
    """Test cases for System API."""
    
    def test_health_check(self, client, mock_services):
        """Test system health check."""
        # Mock all service checks to return healthy status
        mock_services['excel'].load_kitchen_config.return_value = {"KITCHEN_A": {}}
        mock_services['queue'].get_all_kitchen_statuses.return_value = []
        mock_services['starvation'].get_starvation_statistics.return_value = {"currently_starving": 0}
        mock_services['performance'].identify_bottlenecks.return_value = []
        
        response = client.get("/api/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data
        assert "components" in data
    
    def test_reload_config(self, client, mock_services):
        """Test configuration reload."""
        reload_data = {
            "force_reload": True,
            "clear_cache": True
        }
        
        response = client.post("/api/system/reload-config", json=reload_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reloaded_components" in data
    
    def test_get_system_metrics(self, client, mock_services):
        """Test getting system metrics."""
        mock_services['queue'].get_all_kitchen_statuses.return_value = []
        mock_services['starvation'].get_starvation_statistics.return_value = {}
        mock_services['performance'].identify_bottlenecks.return_value = []
        
        response = client.get("/api/system/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data
    
    def test_get_learning_report(self, client, mock_services):
        """Test getting learning report."""
        mock_services['performance'].generate_learning_report.return_value = {
            "system_performance": {},
            "recommendations": []
        }
        
        response = client.get("/api/system/learning-report")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "report" in data
    
    def test_get_current_config(self, client, mock_services):
        """Test getting current configuration."""
        response = client.get("/api/system/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "config" in data


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/api/non-existent-endpoint")
        assert response.status_code == 404
    
    def test_validation_error_handling(self, client, mock_services):
        """Test validation error handling."""
        # Send invalid JSON data
        response = client.post("/api/orders/", json={"invalid": "data"})
        assert response.status_code == 422  # Validation error
    
    def test_internal_error_handling(self, client, mock_services):
        """Test internal error handling."""
        # Mock service to raise exception
        mock_services['excel'].validate_order_items.side_effect = Exception("Test error")
        
        order_data = {"items": ["ITM_001"]}
        response = client.post("/api/orders/", json=order_data)
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
