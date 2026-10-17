"""
Test configuration and fixtures for the Smart Kitchen Queue Management System.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from app.services.excel_service import ExcelDataService
from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.services.performance_learning import PerformanceLearning
from app.services.realtime_updater import RealTimeUpdater
from app.models import QueueItem, PriorityLevel, ItemStatus, Order, OrderStatus


@pytest.fixture
def temp_excel_file():
    """Create a temporary Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        # Create sample Excel file
        from app.utils.excel_creator import create_sample_excel
        create_sample_excel(tmp_file.name)
        yield tmp_file.name
    
    # Cleanup
    if os.path.exists(tmp_file.name):
        os.unlink(tmp_file.name)


@pytest.fixture
def excel_service(temp_excel_file):
    """Create ExcelDataService instance with test data."""
    return ExcelDataService(temp_excel_file)


@pytest.fixture
def queue_manager(excel_service):
    """Create KitchenQueueManager instance."""
    return KitchenQueueManager(excel_service)


@pytest.fixture
def starvation_prevention():
    """Create StarvationPrevention instance."""
    return StarvationPrevention(max_delays=3)


@pytest.fixture
def performance_learning(excel_service):
    """Create PerformanceLearning instance."""
    return PerformanceLearning(excel_service)


@pytest.fixture
def mock_ai_agent():
    """Create mock AI agent for testing."""
    mock_agent = Mock()
    mock_agent.optimize_order_schedule.return_value = Mock(
        order_id="TEST_ORDER",
        optimized_items=[],
        total_estimated_time=30,
        synchronization_achieved=True,
        anti_starvation_applied=[],
        optimization_notes="Test optimization"
    )
    mock_agent.reoptimize_pending_orders.return_value = []
    mock_agent.emergency_reschedule.return_value = {"status": "completed"}
    return mock_agent


@pytest.fixture
def realtime_updater(queue_manager, starvation_prevention, mock_ai_agent, performance_learning):
    """Create RealTimeUpdater instance."""
    updater = RealTimeUpdater(
        queue_manager, starvation_prevention, mock_ai_agent, performance_learning
    )
    yield updater
    # Cleanup
    updater.stop_background_monitoring()


@pytest.fixture
def sample_queue_item():
    """Create a sample queue item for testing."""
    return QueueItem(
        item_id="ITM_001",
        item_name="Grilled Chicken",
        order_id="ORD_TEST",
        prep_time=15,
        scheduled_start=datetime.now(),
        estimated_completion=datetime.now() + timedelta(minutes=15),
        priority_level=PriorityLevel.NORMAL,
        starvation_count=0,
        status=ItemStatus.QUEUED,
        kitchen_id="KITCHEN_A"
    )


@pytest.fixture
def sample_order():
    """Create a sample order for testing."""
    return Order(
        order_id="ORD_TEST",
        items=["ITM_001", "ITM_004", "ITM_007"],
        timestamp=datetime.now(),
        status=OrderStatus.PENDING
    )


@pytest.fixture
def mock_ollama():
    """Mock Ollama LLM for testing."""
    mock_llm = Mock()
    mock_llm.return_value = "Test AI response"
    return mock_llm


@pytest.fixture
def kitchen_configs():
    """Sample kitchen configurations."""
    return {
        "KITCHEN_A": {
            "kitchen_id": "KITCHEN_A",
            "kitchen_name": "Grill Station",
            "capacity": 3,
            "specialization": "Grilled Items",
            "status": "active"
        },
        "KITCHEN_B": {
            "kitchen_id": "KITCHEN_B",
            "kitchen_name": "Pasta Station",
            "capacity": 2,
            "specialization": "Pasta & Rice",
            "status": "active"
        },
        "KITCHEN_C": {
            "kitchen_id": "KITCHEN_C",
            "kitchen_name": "Dessert Station",
            "capacity": 4,
            "specialization": "Desserts & Beverages",
            "status": "active"
        }
    }


@pytest.fixture
def menu_items():
    """Sample menu items."""
    return {
        "ITM_001": {
            "item_id": "ITM_001",
            "item_name": "Grilled Chicken",
            "kitchen_id": "KITCHEN_A",
            "prep_time_minutes": 15,
            "difficulty_level": "medium",
            "available": True
        },
        "ITM_004": {
            "item_id": "ITM_004",
            "item_name": "Spaghetti Bolognese",
            "kitchen_id": "KITCHEN_B",
            "prep_time_minutes": 18,
            "difficulty_level": "high",
            "available": True
        },
        "ITM_007": {
            "item_id": "ITM_007",
            "item_name": "Chocolate Cake",
            "kitchen_id": "KITCHEN_C",
            "prep_time_minutes": 25,
            "difficulty_level": "high",
            "available": True
        }
    }


# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def create_test_queue_items(count: int, kitchen_id: str = "KITCHEN_A") -> list:
        """Create multiple test queue items."""
        items = []
        for i in range(count):
            item = QueueItem(
                item_id=f"ITM_{i:03d}",
                item_name=f"Test Item {i}",
                order_id=f"ORD_{i:03d}",
                prep_time=10 + (i % 20),
                scheduled_start=datetime.now() + timedelta(minutes=i * 5),
                estimated_completion=datetime.now() + timedelta(minutes=(i * 5) + 15),
                priority_level=PriorityLevel.NORMAL,
                starvation_count=0,
                status=ItemStatus.QUEUED,
                kitchen_id=kitchen_id
            )
            items.append(item)
        return items
    
    @staticmethod
    def create_starving_item(item_id: str = "STARVING_ITEM", delay_count: int = 5) -> QueueItem:
        """Create a starving queue item."""
        return QueueItem(
            item_id=item_id,
            item_name="Starving Test Item",
            order_id="STARVING_ORDER",
            prep_time=15,
            scheduled_start=datetime.now() - timedelta(minutes=30),
            estimated_completion=datetime.now() - timedelta(minutes=15),
            priority_level=PriorityLevel.EMERGENCY,
            starvation_count=delay_count,
            status=ItemStatus.QUEUED,
            kitchen_id="KITCHEN_A"
        )


@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils
