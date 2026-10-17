"""
LangChain AI Tools for the Smart Kitchen Queue Management System.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.excel_service import ExcelDataService
from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.models import QueueItem, PriorityLevel, ItemStatus
from pydantic import PrivateAttr

logger = logging.getLogger(__name__)


class OrderAnalyzerInput(BaseModel):
    """Input schema for Order Analyzer Tool."""

    order_items: List[str] = Field(..., description="List of item IDs in the order")
    order_id: str = Field(..., description="Unique order identifier")


class OrderAnalyzerTool(BaseTool):
    """Tool to analyze orders and extract kitchen assignments."""

    name: str = "order_analyzer"
    description: str = "Analyzes order items and validates them against the menu, extracting kitchen assignments"
    args_schema: type = OrderAnalyzerInput
    excel_service: ExcelDataService

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, excel_service: ExcelDataService, **kwargs):
        super().__init__(excel_service=excel_service, **kwargs)

    def _run(self, order_items: List[str], order_id: str) -> str:
        """Analyze order and return kitchen assignments."""
        try:
            # Validate items exist and are available
            if not self.excel_service.validate_order_items(order_items):
                return json.dumps(
                    {
                        "success": False,
                        "error": "Invalid or unavailable items in order",
                        "order_id": order_id,
                    }
                )

            # Get menu items and kitchen assignments
            menu_items = self.excel_service.load_menu_items()
            kitchen_assignments = {}
            total_prep_time = 0

            for item_id in order_items:
                item = menu_items[item_id]
                kitchen_id = item["kitchen_id"]

                if kitchen_id not in kitchen_assignments:
                    kitchen_assignments[kitchen_id] = []

                kitchen_assignments[kitchen_id].append(
                    {
                        "item_id": item_id,
                        "item_name": item["item_name"],
                        "prep_time": item["prep_time_minutes"],
                        "difficulty": item["difficulty_level"],
                    }
                )

                total_prep_time += item["prep_time_minutes"]

            result = {
                "success": True,
                "order_id": order_id,
                "kitchen_assignments": kitchen_assignments,
                "total_items": len(order_items),
                "total_prep_time": total_prep_time,
                "kitchens_involved": list(kitchen_assignments.keys()),
            }

            logger.info(
                f"Analyzed order {order_id}: {len(kitchen_assignments)} kitchens, {total_prep_time} min total"
            )
            return json.dumps(result)

        except Exception as e:
            logger.error(f"Error analyzing order {order_id}: {e}")
            return json.dumps({"success": False, "error": str(e), "order_id": order_id})


class KitchenLoadAssessorInput(BaseModel):
    """Input schema for Kitchen Load Assessor Tool."""

    include_predictions: bool = Field(
        True, description="Whether to include load predictions"
    )


class KitchenLoadAssessor(BaseTool):
    """Tool to assess current kitchen loads and capacities."""

    name: str = "kitchen_load_assessor"
    description: str = "Assesses current kitchen loads, capacities, and availability"
    args_schema: type = KitchenLoadAssessorInput
    queue_manager: KitchenQueueManager
    excel_service: ExcelDataService

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, queue_manager: KitchenQueueManager, excel_service: ExcelDataService, **kwargs
    ):
        super().__init__(queue_manager=queue_manager, excel_service=excel_service, **kwargs)

    def _run(self, include_predictions: bool = True) -> str:
        """Assess current kitchen loads."""
        try:
            kitchen_statuses = self.queue_manager.get_all_kitchen_statuses()
            load_patterns = self.excel_service.load_kitchen_load_patterns()
            current_hour = datetime.now().hour

            assessment = {
                "timestamp": datetime.now().isoformat(),
                "kitchens": {},
                "overall_capacity_utilization": 0,
                "bottleneck_kitchens": [],
            }

            total_capacity = 0
            total_load = 0

            for status in kitchen_statuses:
                kitchen_id = status.kitchen_id
                utilization = (
                    status.current_load / status.capacity if status.capacity > 0 else 0
                )

                kitchen_info = {
                    "kitchen_id": kitchen_id,
                    "kitchen_name": status.kitchen_name,
                    "current_load": status.current_load,
                    "capacity": status.capacity,
                    "available_slots": status.available_slots,
                    "utilization_percentage": utilization * 100,
                    "next_available_time": status.next_available_time.isoformat(),
                    "queue_length": len(status.current_queue),
                    "status": status.status,
                }

                # Add predictions if requested
                if include_predictions:
                    # Get historical load pattern for current hour
                    pattern_col = f"kitchen_{kitchen_id.split('_')[1].lower()}_avg_load"
                    if pattern_col in load_patterns.columns:
                        pattern_row = load_patterns[
                            load_patterns["hour"] == current_hour
                        ]
                        if not pattern_row.empty:
                            expected_load = pattern_row[pattern_col].iloc[0]
                            kitchen_info["expected_load"] = expected_load
                            kitchen_info["load_variance"] = (
                                status.current_load - expected_load
                            )

                assessment["kitchens"][kitchen_id] = kitchen_info

                # Track bottlenecks (>80% utilization)
                if utilization > 0.8:
                    assessment["bottleneck_kitchens"].append(kitchen_id)

                total_capacity += status.capacity
                total_load += status.current_load

            assessment["overall_capacity_utilization"] = (
                (total_load / total_capacity * 100) if total_capacity > 0 else 0
            )

            logger.info(
                f"Kitchen load assessment: {total_load}/{total_capacity} capacity used"
            )
            return json.dumps(assessment)

        except Exception as e:
            logger.error(f"Error assessing kitchen loads: {e}")
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )


class SchedulingOptimizerInput(BaseModel):
    """Input schema for Scheduling Optimizer Tool."""

    order_items: List[str] = Field(..., description="List of item IDs to schedule")
    order_id: str = Field(..., description="Order identifier")
    kitchen_loads: Dict = Field(..., description="Current kitchen load information")
    priority_overrides: Dict[str, str] = Field(
        default_factory=dict, description="Priority overrides for specific items"
    )


class SchedulingOptimizer(BaseTool):
    """Tool to optimize scheduling using historical data and current loads."""

    name: str = "scheduling_optimizer"
    description: str = "Optimizes item scheduling based on historical data, current loads, and constraints"
    args_schema: type = SchedulingOptimizerInput
    excel_service: ExcelDataService
    queue_manager: KitchenQueueManager

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, excel_service: ExcelDataService, queue_manager: KitchenQueueManager, **kwargs
    ):
        super().__init__(excel_service=excel_service, queue_manager=queue_manager, **kwargs)

    def _run(
        self,
        order_items: List[str],
        order_id: str,
        kitchen_loads: Dict,
        priority_overrides: Dict[str, str] = None,
    ) -> str:
        """Optimize scheduling for order items."""
        try:
            menu_items = self.excel_service.load_menu_items()
            historical_data = self.excel_service.load_historical_data()
            priority_overrides = priority_overrides or {}

            # Group items by kitchen
            kitchen_groups = {}
            for item_id in order_items:
                item = menu_items[item_id]
                kitchen_id = item["kitchen_id"]
                if kitchen_id not in kitchen_groups:
                    kitchen_groups[kitchen_id] = []
                kitchen_groups[kitchen_id].append(item_id)

            # Calculate optimal start times for each kitchen
            optimized_schedule = {}
            synchronization_target = None

            for kitchen_id, items in kitchen_groups.items():
                kitchen_schedule = self._optimize_kitchen_schedule(
                    kitchen_id,
                    items,
                    menu_items,
                    historical_data,
                    kitchen_loads,
                    priority_overrides,
                )
                optimized_schedule[kitchen_id] = kitchen_schedule

                # Track latest completion time for synchronization
                for item_schedule in kitchen_schedule:
                    completion_time = item_schedule["estimated_completion"]
                    if (
                        synchronization_target is None
                        or completion_time > synchronization_target
                    ):
                        synchronization_target = completion_time

            # Adjust schedules for synchronization (within 3-minute window)
            synchronized_schedule = self._apply_synchronization(
                optimized_schedule, synchronization_target
            )

            result = {
                "success": True,
                "order_id": order_id,
                "optimized_schedule": synchronized_schedule,
                "synchronization_target": (
                    synchronization_target.isoformat()
                    if synchronization_target
                    else None
                ),
                "total_kitchens": len(kitchen_groups),
                "optimization_timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"Optimized schedule for order {order_id} across {len(kitchen_groups)} kitchens"
            )
            return json.dumps(result)

        except Exception as e:
            logger.error(f"Error optimizing schedule for order {order_id}: {e}")
            return json.dumps({"success": False, "error": str(e), "order_id": order_id})

    def _optimize_kitchen_schedule(
        self,
        kitchen_id: str,
        items: List[str],
        menu_items: Dict,
        historical_data,
        kitchen_loads: Dict,
        priority_overrides: Dict[str, str],
    ) -> List[Dict]:
        """Optimize schedule for a specific kitchen."""
        kitchen_schedule = []
        current_time = datetime.now()

        # Get kitchen's next available time
        next_available = self.queue_manager.get_next_available_slot(kitchen_id)

        # Sort items by priority and prep time
        item_priorities = []
        for item_id in items:
            item = menu_items[item_id]
            priority = priority_overrides.get(item_id, "normal")

            # Get historical average prep time
            hist_data = historical_data[
                (historical_data["kitchen_id"] == kitchen_id)
                & (historical_data["item_id"] == item_id)
            ]
            avg_prep_time = (
                hist_data["actual_prep_time"].mean()
                if not hist_data.empty
                else item["prep_time_minutes"]
            )

            item_priorities.append(
                {
                    "item_id": item_id,
                    "priority": priority,
                    "prep_time": avg_prep_time,
                    "difficulty": item["difficulty_level"],
                }
            )

        # Sort by priority, then by prep time
        priority_order = {"emergency": 0, "high": 1, "normal": 2, "low": 3}
        item_priorities.sort(
            key=lambda x: (priority_order.get(x["priority"], 2), x["prep_time"])
        )

        # Schedule items
        current_start_time = next_available
        for item_info in item_priorities:
            item_id = item_info["item_id"]
            prep_time = item_info["prep_time"]

            estimated_completion = current_start_time + timedelta(minutes=prep_time)

            kitchen_schedule.append(
                {
                    "item_id": item_id,
                    "item_name": menu_items[item_id]["item_name"],
                    "scheduled_start": current_start_time.isoformat(),
                    "estimated_completion": estimated_completion.isoformat(),
                    "prep_time": prep_time,
                    "priority": item_info["priority"],
                }
            )

            # Update start time for next item (assuming sequential processing)
            current_start_time = estimated_completion

        return kitchen_schedule

    def _apply_synchronization(
        self, optimized_schedule: Dict, target_time: datetime
    ) -> Dict:
        """Apply synchronization to ensure items finish within the target window."""
        sync_window = timedelta(minutes=3)  # 3-minute synchronization window

        for kitchen_id, schedule in optimized_schedule.items():
            for item_schedule in schedule:
                completion_time = datetime.fromisoformat(
                    item_schedule["estimated_completion"]
                )

                # If item finishes too early, delay its start
                if target_time - completion_time > sync_window:
                    delay_needed = target_time - completion_time - sync_window

                    original_start = datetime.fromisoformat(
                        item_schedule["scheduled_start"]
                    )
                    new_start = original_start + delay_needed
                    new_completion = completion_time + delay_needed

                    item_schedule["scheduled_start"] = new_start.isoformat()
                    item_schedule["estimated_completion"] = new_completion.isoformat()
                    item_schedule["synchronization_delay"] = (
                        delay_needed.total_seconds() / 60
                    )

        return optimized_schedule


class AntiStarvationMonitorInput(BaseModel):
    """Input schema for Anti-Starvation Monitor Tool."""

    order_items: List[str] = Field(
        ..., description="List of item IDs to check for starvation"
    )
    order_id: str = Field(..., description="Order identifier")


class AntiStarvationMonitor(BaseTool):
    """Tool to monitor and prevent item starvation."""

    name: str = "anti_starvation_monitor"
    description: str = (
        "Monitors items for starvation and applies priority boosts when needed"
    )
    args_schema: type = AntiStarvationMonitorInput
    starvation_prevention: StarvationPrevention

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, starvation_prevention: StarvationPrevention, **kwargs):
        super().__init__(starvation_prevention=starvation_prevention, **kwargs)

    def _run(self, order_items: List[str], order_id: str) -> str:
        """Monitor items for starvation and apply interventions."""
        try:
            starvation_report = {
                "order_id": order_id,
                "timestamp": datetime.now().isoformat(),
                "items_checked": len(order_items),
                "starving_items": [],
                "priority_boosts_applied": [],
                "recommendations": [],
            }

            for item_id in order_items:
                # Check if item is starving
                is_starving = self.starvation_prevention.check_starvation(item_id)
                delay_info = self.starvation_prevention.get_item_delay_info(item_id)

                if is_starving:
                    starvation_report["starving_items"].append(
                        {
                            "item_id": item_id,
                            "delay_count": delay_info["delay_count"],
                            "first_delay_time": (
                                delay_info["first_delay_time"].isoformat()
                                if delay_info["first_delay_time"]
                                else None
                            ),
                            "time_since_first_delay": delay_info[
                                "time_since_first_delay"
                            ],
                        }
                    )

                    # Apply emergency priority
                    emergency_result = (
                        self.starvation_prevention.apply_emergency_priority(item_id)
                    )
                    if emergency_result["applied"]:
                        starvation_report["priority_boosts_applied"].append(
                            {
                                "item_id": item_id,
                                "boost_config": emergency_result["config"],
                                "delay_count": emergency_result["delay_count"],
                            }
                        )

                        starvation_report["recommendations"].append(
                            f"CRITICAL: Item {item_id} requires immediate processing due to starvation"
                        )

                elif delay_info["delay_count"] > 0:
                    # Item has delays but not starving yet
                    boost_factor = self.starvation_prevention.get_priority_boost_factor(
                        item_id
                    )
                    if boost_factor > 1.0:
                        starvation_report["recommendations"].append(
                            f"Item {item_id} has {delay_info['delay_count']} delays, consider priority boost (factor: {boost_factor})"
                        )

            # Add overall starvation statistics
            stats = self.starvation_prevention.get_starvation_statistics()
            starvation_report["system_statistics"] = stats

            # Generate recommendations based on system state
            if stats["currently_starving"] > 0:
                starvation_report["recommendations"].append(
                    f"ALERT: {stats['currently_starving']} items are currently starving system-wide"
                )

            if stats["total_delayed_items"] > 10:
                starvation_report["recommendations"].append(
                    "WARNING: High number of delayed items detected, consider system optimization"
                )

            logger.info(
                f"Starvation check for order {order_id}: {len(starvation_report['starving_items'])} starving items"
            )
            return json.dumps(starvation_report)

        except Exception as e:
            logger.error(f"Error monitoring starvation for order {order_id}: {e}")
            return json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "order_id": order_id,
                    "timestamp": datetime.now().isoformat(),
                }
            )


class AIToolsManager:
    """Manager class for all AI tools."""

    def __init__(
        self,
        excel_service: ExcelDataService,
        queue_manager: KitchenQueueManager,
        starvation_prevention: StarvationPrevention,
    ):
        """Initialize all AI tools."""
        self.excel_service = excel_service
        self.queue_manager = queue_manager
        self.starvation_prevention = starvation_prevention

        # Initialize tools
        self.order_analyzer = OrderAnalyzerTool(excel_service)
        self.kitchen_load_assessor = KitchenLoadAssessor(queue_manager, excel_service)
        self.scheduling_optimizer = SchedulingOptimizer(excel_service, queue_manager)
        self.anti_starvation_monitor = AntiStarvationMonitor(starvation_prevention)

        logger.info("AI Tools Manager initialized with all tools")

    def get_all_tools(self) -> List[BaseTool]:
        """Get list of all available tools."""
        return [
            self.order_analyzer,
            self.kitchen_load_assessor,
            self.scheduling_optimizer,
            self.anti_starvation_monitor,
        ]

    def get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool by name."""
        tools_map = {
            "order_analyzer": self.order_analyzer,
            "kitchen_load_assessor": self.kitchen_load_assessor,
            "scheduling_optimizer": self.scheduling_optimizer,
            "anti_starvation_monitor": self.anti_starvation_monitor,
        }
        return tools_map.get(tool_name)
