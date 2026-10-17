"""
AI Agent for the Smart Kitchen Queue Management System using Ollama and LangChain.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from langchain_ollama import ChatOllama

from app.config import config
from app.services.ai_tools import AIToolsManager
from app.services.excel_service import ExcelDataService
from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.services.performance_learning import PerformanceLearning
from app.models import QueueItem, PriorityLevel, ItemStatus, ScheduleOptimizationResult

logger = logging.getLogger(__name__)


class KitchenAIAgent:
    """AI Agent for intelligent kitchen queue management and scheduling."""

    def __init__(
        self,
        excel_service: ExcelDataService,
        queue_manager: KitchenQueueManager,
        starvation_prevention: StarvationPrevention,
        performance_learning=None,
    ):
        """Initialize the AI agent."""
        self.excel_service = excel_service
        self.queue_manager = queue_manager
        self.starvation_prevention = starvation_prevention
        self.performance_learning = performance_learning or PerformanceLearning(
            excel_service
        )

        # Initialize Ollama LLM
        try:
            print("**" * 20)
            print("Initializing Ollama LLM for AI decision making")
            print(f"OLLAMA_BASE_URL: {config.OLLAMA_BASE_URL}")
            print(f"OLLAMA_MODEL: {config.OLLAMA_MODEL}")
            print("**" * 20)

            self.llm = ChatOllama(
                base_url=config.OLLAMA_BASE_URL,
                model=config.OLLAMA_MODEL,
                temperature=0.1,  # Low temperature for consistent scheduling decisions
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama: {e}. Using mock AI.")
            self.llm = ChatOllama()  # Mock version

        # Initialize AI tools
        self.tools_manager = AIToolsManager(
            excel_service, queue_manager, starvation_prevention
        )

        # Simple conversation history
        self.conversation_history = []

        logger.info("Kitchen AI Agent initialized successfully")

    async def optimize_order_schedule(
        self, order_items: List[str], order_id: str
    ) -> ScheduleOptimizationResult:
        """Optimize scheduling for a new order using AI decision making."""
        try:
            # Gather system context for AI decision making
            context = await self._gather_system_context(order_items, order_id)

            # Create intelligent scheduling prompt
            prompt = self._create_intelligent_scheduling_prompt(
                context, order_items, order_id
            )

            # Get AI decision using LLM
            ai_response = self.llm.invoke(prompt)

            # Parse AI response and create optimized schedule
            optimization_result = await self._parse_ai_scheduling_response(
                ai_response, order_items, order_id, context
            )

            # Store conversation for learning
            self.conversation_history.append(
                {
                    "prompt": prompt,
                    "response": ai_response,
                    "order_id": order_id,
                    "timestamp": datetime.now(),
                }
            )

            logger.info(
                f"AI optimization completed for order {order_id} using LLM decision making"
            )
            return optimization_result

        except Exception as e:
            logger.error(f"Error in AI optimization for order {order_id}: {e}")
            # Fallback to basic scheduling
            return await self._fallback_scheduling(order_items, order_id)

    def _create_scheduling_prompt(self, order_items: List[str], order_id: str) -> str:
        """Create the scheduling prompt for the AI agent."""

        # Get current system status
        kitchen_statuses = self.queue_manager.get_all_kitchen_statuses()
        starvation_stats = self.starvation_prevention.get_starvation_statistics()

        # Format kitchen status information
        kitchen_status_info = []
        for status in kitchen_statuses:
            kitchen_status_info.append(
                f"Kitchen {status.kitchen_id} ({status.kitchen_name}): "
                f"Load {status.current_load}/{status.capacity}, "
                f"Available slots: {status.available_slots}, "
                f"Next available: {status.next_available_time.strftime('%H:%M')}"
            )

        # Format starvation information
        starving_items = starvation_stats.get("emergency_items", [])
        starvation_info = f"Currently starving items: {len(starving_items)}"
        if starving_items:
            starvation_info += f" - Items: {', '.join(starving_items)}"

        prompt = f"""
You are an intelligent kitchen queue management system. Your task is to optimize food preparation scheduling across multiple kitchens.

CURRENT STATUS:
{chr(10).join(kitchen_status_info)}

NEW ORDER: {order_id}
Items to schedule: {', '.join(order_items)}

STARVATION STATUS: {starvation_info}
Total delayed items: {starvation_stats.get('total_delayed_items', 0)}

OPTIMIZATION RULES:
1. Minimize total order completion time
2. Ensure items finish within 2-3 minutes of each other for synchronized delivery
3. Utilize kitchen capacities efficiently without overloading
4. CRITICAL: Prevent item starvation - if an item has been delayed {config.MAX_STARVATION_COUNT}+ times, give it EMERGENCY priority
5. Consider historical prep time variations and kitchen efficiency
6. Balance kitchen loads to prevent bottlenecks

REQUIRED ACTIONS:
1. Use the order_analyzer tool to validate items and get kitchen assignments
2. Use the kitchen_load_assessor tool to get detailed current loads
3. Use the anti_starvation_monitor tool to check for starving items
4. Use the scheduling_optimizer tool to create the optimal schedule
5. Never Give Name/ID of kitchen or Item out of context 

Please analyze this order and provide an optimized schedule that follows all rules and prevents starvation.
Focus on efficiency while ensuring no item is left behind.

Return your final recommendation in JSON format with:
- optimized_schedule: detailed schedule for each kitchen
- synchronization_achieved: boolean
- anti_starvation_applied: list of items with emergency priority
- total_estimated_time: minutes until all items complete
- optimization_notes: explanation of decisions made
"""

        return prompt

    async def _gather_system_context(
        self, order_items: List[str], order_id: str
    ) -> Dict[str, Any]:
        """Gather comprehensive system context for AI decision making."""
        try:
            # Get current kitchen statuses
            kitchen_statuses = await self.queue_manager.get_all_kitchen_statuses()

            # Get menu item details from MongoDB
            menu_items_list = await self.queue_manager.mongodb_service.get_menu_items()
            menu_items = {item['item_id']: item for item in menu_items_list}
            order_item_details = {
                item_id: menu_items.get(item_id, {}) for item_id in order_items
            }

            # Get starvation statistics
            starvation_stats = self.starvation_prevention.get_starvation_statistics()

            # Get historical performance data
            historical_data = self.excel_service.load_historical_data()
            recent_performance = (
                historical_data.tail(50) if not historical_data.empty else None
            )

            # Calculate current system load
            total_capacity = sum(status.capacity for status in kitchen_statuses)
            total_load = sum(status.current_load for status in kitchen_statuses)
            system_utilization = (
                (total_load / total_capacity * 100) if total_capacity > 0 else 0
            )

            # Identify bottlenecks
            bottlenecks = self.performance_learning.identify_bottlenecks()

            context = {
                "order_id": order_id,
                "order_items": order_item_details,
                "kitchen_statuses": [
                    {
                        "kitchen_id": status.kitchen_id,
                        "kitchen_name": status.kitchen_name,
                        "capacity": status.capacity,
                        "current_load": status.current_load,
                        "available_slots": status.available_slots,
                        "queue_length": len(status.current_queue),
                        "next_available_time": status.next_available_time.strftime(
                            "%H:%M:%S"
                        ),
                        "specialization": status.specialization,
                    }
                    for status in kitchen_statuses
                ],
                "system_metrics": {
                    "total_capacity": total_capacity,
                    "total_load": total_load,
                    "utilization_percentage": round(system_utilization, 2),
                    "currently_starving": starvation_stats.get("currently_starving", 0),
                    "total_delayed_items": starvation_stats.get(
                        "total_delayed_items", 0
                    ),
                },
                "bottlenecks": bottlenecks,
                "current_time": datetime.now().strftime("%H:%M:%S"),
                "recent_performance_summary": (
                    self._summarize_recent_performance(recent_performance)
                    if recent_performance is not None
                    else None
                ),
            }

            return context

        except Exception as e:
            logger.error(f"Error gathering system context: {e}")
            return {"error": str(e), "order_id": order_id, "order_items": order_items}

    def _summarize_recent_performance(self, recent_data) -> Dict[str, Any]:
        """Summarize recent performance data for AI context."""
        try:
            if recent_data.empty:
                return {"message": "No recent performance data available"}

            summary = {
                "total_items_processed": len(recent_data),
                "avg_actual_prep_time": round(
                    recent_data["actual_prep_time"].mean(), 2
                ),
                "avg_scheduled_prep_time": round(
                    recent_data["scheduled_prep_time"].mean(), 2
                ),
                "avg_delay": round(recent_data["delay_minutes"].mean(), 2),
                "on_time_percentage": round(
                    len(recent_data[recent_data["delay_minutes"] == 0])
                    / len(recent_data)
                    * 100,
                    2,
                ),
                "kitchen_performance": recent_data.groupby("kitchen_id")
                .agg({"actual_prep_time": "mean", "delay_minutes": "mean"})
                .round(2)
                .to_dict(),
            }

            return summary

        except Exception as e:
            logger.error(f"Error summarizing performance: {e}")
            return {"error": str(e)}

    def _create_intelligent_scheduling_prompt(
        self, context: Dict[str, Any], order_items: List[str], order_id: str
    ) -> str:
        """Create an intelligent prompt for the LLM to make scheduling decisions."""

        # Format kitchen status information
        kitchen_info = []
        for kitchen in context.get("kitchen_statuses", []):
            kitchen_info.append(
                f"- {kitchen['kitchen_name']} (ID: {kitchen['kitchen_id']}): "
                f"Load {kitchen['current_load']}/{kitchen['capacity']}, "
                f"Available slots: {kitchen['available_slots']}, "
                f"Queue length: {kitchen['queue_length']}, "
                f"Next available: {kitchen['next_available_time']}, "
                f"Specialization: {kitchen['specialization']}"
            )

        # Format order items information
        order_info = []
        for item_id, item_details in context.get("order_items", {}).items():
            if item_details:
                order_info.append(
                    f"- {item_details.get('item_name', item_id)} (ID: {item_id}): "
                    f"Kitchen: {item_details.get('kitchen_id', 'Unknown')}, "
                    f"Prep time: {item_details.get('prep_time_minutes', 0)} min, "
                    f"Difficulty: {item_details.get('difficulty_level', 'Unknown')}"
                )

        # Format system metrics
        metrics = context.get("system_metrics", {})

        # Format bottlenecks
        bottlenecks_info = "None identified"
        if context.get("bottlenecks"):
            bottlenecks_info = ", ".join(
                [
                    f"{b.get('type', 'Unknown')} ({b.get('severity', 'medium')} severity)"
                    for b in context.get("bottlenecks", [])
                ]
            )

        # Format recent performance
        perf_summary = context.get("recent_performance_summary", {})
        performance_info = "No recent data available"
        if perf_summary and "error" not in perf_summary:
            performance_info = (
                f"Recent performance: {perf_summary.get('total_items_processed', 0)} items processed, "
                f"avg delay: {perf_summary.get('avg_delay', 0)} min, "
                f"on-time rate: {perf_summary.get('on_time_percentage', 0)}%"
            )

        prompt = f"""
You are an intelligent kitchen queue management AI. Your task is to optimize the scheduling of a new order across multiple specialized kitchens.

CURRENT SYSTEM STATUS (Time: {context.get('current_time', 'Unknown')}):
System Utilization: {metrics.get('utilization_percentage', 0)}% ({metrics.get('total_load', 0)}/{metrics.get('total_capacity', 0)})
Currently Starving Items: {metrics.get('currently_starving', 0)}
Total Delayed Items: {metrics.get('total_delayed_items', 0)}

KITCHEN STATUS:
{chr(10).join(kitchen_info)}

NEW ORDER TO SCHEDULE:
Order ID: {order_id}
Items:
{chr(10).join(order_info)}

SYSTEM PERFORMANCE:
{performance_info}

CURRENT BOTTLENECKS:
{bottlenecks_info}

OPTIMIZATION OBJECTIVES:
1. CRITICAL: Prevent item starvation - items delayed {config.MAX_STARVATION_COUNT}+ times get EMERGENCY priority
2. Minimize total order completion time
3. Ensure items finish within 2-3 minutes of each other for synchronized delivery
4. Balance kitchen loads efficiently
5. Consider historical performance patterns
6. Respect kitchen capacities and specializations

DECISION REQUIRED:
Analyze the current situation and provide an optimal scheduling decision. Consider:
- Which kitchen should handle each item?
- What priority level should each item have?
- What is the optimal start time for each item?
- How can we achieve synchronization?
- Are there any starvation risks to address?

Respond with a JSON object containing your scheduling decision:
{{
    "analysis": "Your reasoning for the scheduling decisions",
    "total_estimated_time": <total minutes for order completion>,
    "synchronization_achieved": <true/false>,
    "items_schedule": [
        {{
            "item_id": "<item_id>",
            "item_name": "<item_name>",
            "assigned_kitchen": "<kitchen_id>",
            "priority_level": "<emergency/high/normal/low>",
            "scheduled_start_offset": <minutes from now>,
            "estimated_prep_time": <minutes>,
            "reasoning": "Why this scheduling decision was made"
        }}
    ],
    "anti_starvation_actions": [
        {{
            "item_id": "<item_id>",
            "action": "emergency_priority",
            "reason": "Item has been delayed X times"
        }}
    ],
    "optimization_notes": "Summary of key optimization decisions and trade-offs"
}}

Make intelligent decisions based on the current system state, performance history, and optimization objectives.
[IMPORTANT] No Prefix or suffix or any kind of explanation required just JSON response.
"""

        return prompt

    async def _parse_ai_scheduling_response(
        self,
        ai_response: str,
        order_items: List[str],
        order_id: str,
        context: Dict[str, Any],
    ) -> ScheduleOptimizationResult:
        """Parse the AI's intelligent scheduling response and create queue items."""
        try:
            # Extract JSON from AI response
            ai_response = ai_response.content
            print("-----------------------------------------------------------------------------")
            print("AI RESPONSE:\n", ai_response)
            print("-----------------------------------------------------------------------------")

            json_start = ai_response.find("{")
            json_end = ai_response.rfind("}") + 1

            if json_start == -1 or json_end <= json_start:
                logger.warning("No valid JSON found in AI response, using fallback")
                return await self._fallback_scheduling(order_items, order_id)

            json_str = ai_response[json_start:json_end]
            ai_decision = json.loads(json_str)

            # Create optimized queue items based on AI decision
            optimized_items = []
            anti_starvation_applied = []

            menu_items = self.excel_service.load_menu_items()
            current_time = datetime.now()

            for item_schedule in ai_decision.get("items_schedule", []):
                item_id = item_schedule.get("item_id")
                if not item_id or item_id not in menu_items:
                    continue

                item_details = menu_items[item_id]
                kitchen_id = item_schedule.get(
                    "assigned_kitchen", item_details.get("kitchen_id")
                )

                # Parse priority level
                priority_str = item_schedule.get("priority_level", "normal").lower()
                priority_map = {
                    "emergency": PriorityLevel.EMERGENCY,
                    "high": PriorityLevel.HIGH,
                    "normal": PriorityLevel.NORMAL,
                    "low": PriorityLevel.LOW,
                }
                priority_level = priority_map.get(priority_str, PriorityLevel.NORMAL)

                # Calculate timing
                start_offset = item_schedule.get("scheduled_start_offset", 0)
                scheduled_start = current_time + timedelta(minutes=start_offset)
                prep_time = item_schedule.get(
                    "estimated_prep_time", item_details.get("prep_time_minutes", 15)
                )
                estimated_completion = scheduled_start + timedelta(minutes=prep_time)

                # Check for starvation count
                starvation_count = self.starvation_prevention.get_item_delay_info(
                    item_id
                )["delay_count"]

                # Apply anti-starvation boost if AI detected starvation risk
                if (
                    priority_level == PriorityLevel.EMERGENCY
                    or starvation_count >= config.MAX_STARVATION_COUNT
                ):
                    anti_starvation_applied.append(item_id)
                    priority_level = PriorityLevel.EMERGENCY
                    # Apply starvation boost
                    boosted_item = (
                        self.starvation_prevention.apply_starvation_boost_to_queue_item(
                            QueueItem(
                                item_id=item_id,
                                item_name=item_details.get("item_name", item_id),
                                order_id=order_id,
                                prep_time=prep_time,
                                scheduled_start=scheduled_start,
                                estimated_completion=estimated_completion,
                                priority_level=priority_level,
                                starvation_count=starvation_count,
                                status=ItemStatus.QUEUED,
                                kitchen_id=kitchen_id,
                            )
                        )
                    )
                    optimized_items.append(boosted_item)
                else:
                    # Create normal queue item
                    queue_item = QueueItem(
                        item_id=item_id,
                        item_name=item_details.get("item_name", item_id),
                        order_id=order_id,
                        prep_time=prep_time,
                        scheduled_start=scheduled_start,
                        estimated_completion=estimated_completion,
                        priority_level=priority_level,
                        starvation_count=starvation_count,
                        status=ItemStatus.QUEUED,
                        kitchen_id=kitchen_id,
                    )
                    optimized_items.append(queue_item)

            # Create optimization result
            result = ScheduleOptimizationResult(
                order_id=order_id,
                optimized_items=optimized_items,
                total_estimated_time=ai_decision.get("total_estimated_time", 0),
                synchronization_achieved=ai_decision.get(
                    "synchronization_achieved", False
                ),
                anti_starvation_applied=anti_starvation_applied,
                optimization_notes=f"AI Decision: {ai_decision.get('analysis', 'No analysis provided')}. {ai_decision.get('optimization_notes', '')}",
            )

            logger.info(
                f"AI successfully optimized order {order_id}: {len(optimized_items)} items, sync: {result.synchronization_achieved}"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            logger.debug(f"AI response was: {ai_response}")
            return await self._fallback_scheduling(order_items, order_id)
        except Exception as e:
            logger.error(f"Error parsing AI scheduling response: {e}")
            return await self._fallback_scheduling(order_items, order_id)

    async def _parse_tool_response(
        self, response: str, order_items: List[str], order_id: str
    ) -> ScheduleOptimizationResult:
        """Parse tool response and create optimization result."""
        try:
            import json

            if isinstance(response, str):
                # Try to extract JSON from the response
                json_start = response.find("{")
                json_end = response.rfind("}") + 1

                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    tool_result = json.loads(json_str)
                else:
                    # Fallback if no JSON found
                    logger.warning("No JSON found in tool response, using fallback")
                    return await self._fallback_scheduling(order_items, order_id)
            else:
                tool_result = response

            # Create queue items from tool result
            optimized_items = []
            anti_starvation_applied = tool_result.get("anti_starvation_applied", [])

            # Use fallback scheduling with tool insights
            return await self._fallback_scheduling(order_items, order_id, tool_result)

        except Exception as e:
            logger.error(f"Error parsing tool response: {e}")
            return await self._fallback_scheduling(order_items, order_id)

    async def _parse_ai_response(
        self, response: str, order_items: List[str], order_id: str
    ) -> ScheduleOptimizationResult:
        """Parse AI response and create optimization result."""
        try:
            # Try to extract JSON from the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                ai_result = json.loads(json_str)
            else:
                # Fallback if no JSON found
                logger.warning("No JSON found in AI response, using fallback")
                return await self._fallback_scheduling(order_items, order_id)

            # Create queue items from AI schedule
            optimized_items = []
            anti_starvation_applied = ai_result.get("anti_starvation_applied", [])

            for kitchen_id, kitchen_schedule in ai_result.get(
                "optimized_schedule", {}
            ).items():
                for item_schedule in kitchen_schedule:
                    item_id = item_schedule["item_id"]

                    # Determine priority
                    priority = PriorityLevel.NORMAL
                    if item_id in anti_starvation_applied:
                        priority = PriorityLevel.EMERGENCY
                    elif item_schedule.get("priority") == "high":
                        priority = PriorityLevel.HIGH
                    elif item_schedule.get("priority") == "low":
                        priority = PriorityLevel.LOW

                    # Create queue item
                    queue_item = QueueItem(
                        item_id=item_id,
                        item_name=item_schedule["item_name"],
                        order_id=order_id,
                        prep_time=int(item_schedule["prep_time"]),
                        scheduled_start=datetime.fromisoformat(
                            item_schedule["scheduled_start"]
                        ),
                        estimated_completion=datetime.fromisoformat(
                            item_schedule["estimated_completion"]
                        ),
                        priority_level=priority,
                        starvation_count=self.starvation_prevention.get_item_delay_info(
                            item_id
                        )["delay_count"],
                        status=ItemStatus.QUEUED,
                        kitchen_id=kitchen_id,
                    )

                    optimized_items.append(queue_item)

            return ScheduleOptimizationResult(
                order_id=order_id,
                optimized_items=optimized_items,
                total_estimated_time=ai_result.get("total_estimated_time", 0),
                synchronization_achieved=ai_result.get(
                    "synchronization_achieved", False
                ),
                anti_starvation_applied=anti_starvation_applied,
                optimization_notes=ai_result.get(
                    "optimization_notes", "AI optimization completed"
                ),
            )

        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return await self._fallback_scheduling(order_items, order_id)

    async def _fallback_scheduling(
        self, order_items: List[str], order_id: str, tool_insights: dict = None
    ) -> ScheduleOptimizationResult:
        """Fallback scheduling when AI fails."""
        logger.warning(f"Using fallback scheduling for order {order_id}")

        try:
            # Get menu items from MongoDB
            menu_items_list = await self.queue_manager.mongodb_service.get_menu_items()
            menu_items = {item['item_id']: item for item in menu_items_list}
            optimized_items = []
            current_time = datetime.now()

            for item_id in order_items:
                item = menu_items[item_id]
                kitchen_id = item["kitchen_id"]

                # Check for starvation
                priority = PriorityLevel.NORMAL
                if self.starvation_prevention.check_starvation(item_id):
                    priority = PriorityLevel.EMERGENCY

                # Get next available slot
                start_time = await self.queue_manager.get_next_available_slot(kitchen_id)
                completion_time = start_time + timedelta(
                    minutes=item.get("prep_time_minutes", item.get("prep_time", 10))
                )

                queue_item = QueueItem(
                    item_id=item_id,
                    item_name=item.get("item_name", item.get("name", item_id)),
                    order_id=order_id,
                    prep_time=item.get("prep_time_minutes", item.get("prep_time", 10)),
                    scheduled_start=start_time,
                    estimated_completion=completion_time,
                    priority_level=priority,
                    starvation_count=self.starvation_prevention.get_item_delay_info(
                        item_id
                    )["delay_count"],
                    status=ItemStatus.QUEUED,
                    kitchen_id=kitchen_id,
                )

                optimized_items.append(queue_item)

            # Calculate total time
            if optimized_items:
                total_time = max(
                    (item.estimated_completion - current_time).total_seconds() / 60
                    for item in optimized_items
                )
            else:
                total_time = 0

            return ScheduleOptimizationResult(
                order_id=order_id,
                optimized_items=optimized_items,
                total_estimated_time=int(total_time),
                synchronization_achieved=False,
                anti_starvation_applied=[],
                optimization_notes="Fallback scheduling used due to AI error",
            )

        except Exception as e:
            logger.error(f"Error in fallback scheduling: {e}")
            raise

    def reoptimize_pending_orders(self) -> List[ScheduleOptimizationResult]:
        """Reoptimize all pending orders when system state changes."""
        try:
            # Get all pending orders from queue manager
            all_statuses = self.queue_manager.get_all_kitchen_statuses()
            pending_orders = {}

            # Group queue items by order
            for status in all_statuses:
                for item in status.current_queue:
                    if item.status == ItemStatus.QUEUED:
                        if item.order_id not in pending_orders:
                            pending_orders[item.order_id] = []
                        pending_orders[item.order_id].append(item.item_id)

            # Reoptimize each pending order
            reoptimization_results = []
            for order_id, items in pending_orders.items():
                result = self.optimize_order_schedule(items, order_id)
                reoptimization_results.append(result)

            logger.info(f"Reoptimized {len(pending_orders)} pending orders")
            return reoptimization_results

        except Exception as e:
            logger.error(f"Error reoptimizing pending orders: {e}")
            return []

    async def get_ai_insights(self) -> Dict[str, Any]:
        """Get AI insights about current system performance using LLM analysis."""
        try:
            # Gather comprehensive system data
            context = await self._gather_system_context([], "SYSTEM_INSIGHTS")

            # Create intelligent insights prompt
            insights_prompt = f"""
You are an intelligent kitchen management analyst. Analyze the current system performance and provide actionable insights.

CURRENT SYSTEM STATUS:
{json.dumps(context, indent=2, default=str)}

ANALYSIS REQUIRED:
1. Overall system efficiency assessment
2. Bottleneck identification and impact analysis
3. Starvation prevention effectiveness
4. Performance trends and patterns
5. Specific recommendations for improvement
6. Risk assessment and mitigation strategies

Provide your analysis in JSON format:
{{
    "overall_assessment": {{
        "efficiency_score": <0-100>,
        "status": "<excellent/good/fair/poor>",
        "key_strengths": ["strength1", "strength2"],
        "main_concerns": ["concern1", "concern2"]
    }},
    "bottleneck_analysis": {{
        "critical_bottlenecks": [
            {{
                "location": "<kitchen_id or system_area>",
                "severity": "<high/medium/low>",
                "impact": "description of impact",
                "root_cause": "identified cause"
            }}
        ],
        "capacity_utilization": {{
            "overloaded_kitchens": ["kitchen_ids"],
            "underutilized_kitchens": ["kitchen_ids"]
        }}
    }},
    "starvation_assessment": {{
        "prevention_effectiveness": "<excellent/good/needs_improvement/critical>",
        "current_risk_level": "<low/medium/high/critical>",
        "items_at_risk": <number>,
        "intervention_success_rate": "<percentage or assessment>"
    }},
    "performance_trends": {{
        "efficiency_trend": "<improving/stable/declining>",
        "delay_trend": "<decreasing/stable/increasing>",
        "throughput_trend": "<increasing/stable/decreasing>"
    }},
    "recommendations": [
        {{
            "priority": "<high/medium/low>",
            "category": "<capacity/process/technology/staffing>",
            "action": "specific recommendation",
            "expected_impact": "description of expected improvement",
            "implementation_effort": "<low/medium/high>"
        }}
    ],
    "risk_assessment": {{
        "immediate_risks": ["risk descriptions"],
        "mitigation_actions": ["action items"],
        "monitoring_points": ["what to watch"]
    }}
}}

Provide intelligent, data-driven insights based on the current system state.
"""

            # Get AI analysis using LLM
            ai_response = self.llm.invoke(insights_prompt)

            # Parse AI insights
            insights = self._parse_ai_insights_response(ai_response)

            # Store for learning
            self.conversation_history.append(
                {
                    "type": "insights_analysis",
                    "prompt": insights_prompt,
                    "response": ai_response,
                    "timestamp": datetime.now(),
                }
            )

            return insights

        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _parse_ai_insights_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI insights response."""
        try:
            ai_response = ai_response.content
            print("-----------------------------------------------------------------------------")
            print("AI RESPONSE:\n", ai_response)
            print("-----------------------------------------------------------------------------")
            # Extract JSON from AI response
            json_start = ai_response.find("{")
            json_end = ai_response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {
                    "status": "analysis_completed",
                    "raw_response": ai_response,
                    "timestamp": datetime.now().isoformat(),
                }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI insights JSON: {e}")
            return {
                "status": "parse_error",
                "error": str(e),
                "raw_response": ai_response,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error parsing AI insights: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def update_learning_data(self, performance_data: Dict):
        """Update the AI's learning data with new performance information."""
        try:
            # Store performance data in Excel
            self.excel_service.update_historical_performance(performance_data)

            # Clear conversation history to incorporate new learning
            self.conversation_history.clear()

            logger.info("AI learning data updated successfully")

        except Exception as e:
            logger.error(f"Error updating AI learning data: {e}")

    async def emergency_reschedule(self, starving_items: List[str]) -> Dict[str, Any]:
        """Emergency rescheduling for starving items using AI decision making."""
        try:
            # Gather emergency context
            context = await self._gather_system_context(
                starving_items, "EMERGENCY_RESCHEDULE"
            )

            # Create emergency rescheduling prompt
            emergency_prompt = f"""
CRITICAL EMERGENCY: KITCHEN QUEUE STARVATION DETECTED

STARVING ITEMS REQUIRING IMMEDIATE INTERVENTION:
{', '.join(starving_items)}

CURRENT SYSTEM STATE:
{json.dumps(context, indent=2, default=str)}

EMERGENCY OBJECTIVES:
1. IMMEDIATE PRIORITY: Prevent further starvation of these items
2. Apply emergency priority and bypass normal scheduling
3. Minimize disruption to other orders while ensuring starving items are processed
4. Identify root causes of starvation
5. Implement preventive measures

REQUIRED EMERGENCY ACTIONS:
Analyze the situation and provide immediate emergency rescheduling decisions:

{{
    "emergency_assessment": {{
        "severity_level": "<critical/high/medium>",
        "root_causes": ["cause1", "cause2"],
        "immediate_risks": ["risk descriptions"],
        "estimated_recovery_time": <minutes>
    }},
    "emergency_actions": [
        {{
            "item_id": "<item_id>",
            "current_delay_count": <number>,
            "emergency_priority": "EMERGENCY",
            "immediate_kitchen_assignment": "<kitchen_id>",
            "bypass_queue": true,
            "estimated_start_time": "<HH:MM>",
            "justification": "why this action is necessary"
        }}
    ],
    "system_adjustments": {{
        "capacity_overrides": [
            {{
                "kitchen_id": "<kitchen_id>",
                "temporary_capacity_increase": <number>,
                "duration_minutes": <number>
            }}
        ],
        "queue_reordering": "description of queue changes needed"
    }},
    "prevention_measures": [
        {{
            "measure": "specific preventive action",
            "implementation": "how to implement",
            "expected_impact": "expected improvement"
        }}
    ],
    "monitoring_plan": {{
        "check_intervals": <minutes>,
        "success_metrics": ["metric1", "metric2"],
        "escalation_triggers": ["trigger conditions"]
    }}
}}

This is a CRITICAL situation requiring immediate intelligent intervention.
"""

            # Get AI emergency decision
            ai_response = self.llm.invoke(emergency_prompt)

            # Parse emergency response
            emergency_result = self._parse_emergency_response(
                ai_response, starving_items
            )

            # Apply emergency actions immediately
            self._execute_emergency_actions(emergency_result, starving_items)

            # Store for learning
            self.conversation_history.append(
                {
                    "type": "emergency_reschedule",
                    "starving_items": starving_items,
                    "prompt": emergency_prompt,
                    "response": ai_response,
                    "timestamp": datetime.now(),
                }
            )

            logger.critical(
                f"AI emergency rescheduling completed for {len(starving_items)} starving items"
            )
            return emergency_result

        except Exception as e:
            logger.error(f"Error in emergency rescheduling: {e}")
            return {
                "status": "error",
                "error": str(e),
                "starving_items": starving_items,
                "timestamp": datetime.now().isoformat(),
            }

    def _parse_emergency_response(
        self, ai_response: str, starving_items: List[str]
    ) -> Dict[str, Any]:
        """Parse AI emergency response."""
        try:
            ai_response = ai_response.content
            print("-----------------------------------------------------------------------------")
            print("AI RESPONSE:\n", ai_response)
            print("-----------------------------------------------------------------------------")
            # Extract JSON from AI response
            json_start = ai_response.find("{")
            json_end = ai_response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                emergency_result = json.loads(json_str)
            else:
                emergency_result = {
                    "status": "emergency_processed",
                    "raw_response": ai_response,
                }

            emergency_result["timestamp"] = datetime.now().isoformat()
            emergency_result["starving_items"] = starving_items

            return emergency_result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse emergency JSON response: {e}")
            return {
                "status": "parse_error",
                "error": str(e),
                "starving_items": starving_items,
                "raw_response": ai_response,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error parsing emergency response: {e}")
            return {
                "status": "error",
                "error": str(e),
                "starving_items": starving_items,
                "timestamp": datetime.now().isoformat(),
            }

    def _execute_emergency_actions(
        self, emergency_result: Dict[str, Any], starving_items: List[str]
    ):
        """Execute the emergency actions determined by AI."""
        try:
            emergency_actions = emergency_result.get("emergency_actions", [])

            for action in emergency_actions:
                item_id = action.get("item_id")
                if not item_id or item_id not in starving_items:
                    continue

                # Apply emergency priority through starvation prevention
                self.starvation_prevention.apply_emergency_priority(item_id)

                # Force immediate scheduling if specified
                if action.get("bypass_queue", False):
                    kitchen_id = action.get("immediate_kitchen_assignment")
                    if kitchen_id:
                        # Try to force schedule in the specified kitchen
                        try:
                            # This would require queue manager to support emergency insertion
                            logger.info(
                                f"Emergency action: Forcing {item_id} to {kitchen_id}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to execute emergency action for {item_id}: {e}"
                            )

            # Apply system adjustments if specified
            system_adjustments = emergency_result.get("system_adjustments", {})
            capacity_overrides = system_adjustments.get("capacity_overrides", [])

            for override in capacity_overrides:
                kitchen_id = override.get("kitchen_id")
                temp_increase = override.get("temporary_capacity_increase", 0)
                duration = override.get("duration_minutes", 30)

                logger.info(
                    f"Emergency capacity override: {kitchen_id} +{temp_increase} for {duration} minutes"
                )
                # This would require queue manager to support temporary capacity increases

            logger.info(f"Executed {len(emergency_actions)} emergency actions")

        except Exception as e:
            logger.error(f"Error executing emergency actions: {e}")

    async def reoptimize_pending_orders(self) -> List[ScheduleOptimizationResult]:
        """Reoptimize all pending orders using AI decision making."""
        try:
            # Get all pending orders from queue manager
            all_statuses = await self.queue_manager.get_all_kitchen_statuses()
            pending_orders = {}

            # Group queue items by order
            for status in all_statuses:
                for item in status.current_queue:
                    if item.status == ItemStatus.QUEUED:
                        if item.order_id not in pending_orders:
                            pending_orders[item.order_id] = []
                        pending_orders[item.order_id].append(item.item_id)

            # Use AI to reoptimize each pending order
            reoptimization_results = []
            for order_id, items in pending_orders.items():
                # Create reoptimization prompt
                context = await self._gather_system_context(items, order_id)

                reopt_prompt = f"""
REOPTIMIZATION REQUEST

Current system state has changed. Reanalyze and optimize the following pending order:

Order ID: {order_id}
Items: {', '.join(items)}

CURRENT SYSTEM STATE:
{json.dumps(context, indent=2, default=str)}

REOPTIMIZATION OBJECTIVES:
1. Adapt to current system conditions
2. Maintain or improve synchronization
3. Address any new starvation risks
4. Optimize based on latest performance data

Provide updated scheduling decisions in the same JSON format as initial optimization.
"""

                # Get AI reoptimization decision
                ai_response = self.llm.invoke(reopt_prompt)

                # Parse and apply reoptimization
                result = await self._parse_ai_scheduling_response(
                    ai_response, items, order_id, context
                )
                reoptimization_results.append(result)

            logger.info(f"AI reoptimized {len(pending_orders)} pending orders")
            return reoptimization_results

        except Exception as e:
            logger.error(f"Error in AI reoptimization: {e}")
            return []
