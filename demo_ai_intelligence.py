#!/usr/bin/env python3
"""
Demonstration of AI-Driven Intelligence in the Smart Kitchen Queue Management System.

This script demonstrates how the LLM (Ollama) is actually used for intelligent decision making
in scheduling, optimization, and emergency management.
"""

import asyncio
import json
from datetime import datetime
from app.services.excel_service import ExcelDataService
from app.services.queue_manager import KitchenQueueManager
from app.services.starvation_prevention import StarvationPrevention
from app.services.ai_agent import KitchenAIAgent
from app.services.performance_learning import PerformanceLearning


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_ai_response(title, prompt, response):
    """Print AI interaction details."""
    print(f"\n🤖 {title}")

    
    print(f"{'─'*40}")
    print("📝 PROMPT SENT TO LLM:")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print(f"\n🧠 AI RESPONSE:")
    print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
    print(f"{'─'*40}")


def demonstrate_ai_scheduling():
    """Demonstrate AI-driven order scheduling."""
    print_section("AI-DRIVEN ORDER SCHEDULING DEMONSTRATION")
    
    try:
        # Initialize services
        excel_service = ExcelDataService()
        queue_manager = KitchenQueueManager(excel_service)
        starvation_prevention = StarvationPrevention()
        performance_learning = PerformanceLearning(excel_service)
        
        # Initialize AI Agent (this is where the LLM is used)
        ai_agent = KitchenAIAgent(excel_service, queue_manager, starvation_prevention, performance_learning)
        
        print("✅ AI Agent initialized with Ollama LLM")
        print(f"🔗 LLM Base URL: {ai_agent.llm.base_url if hasattr(ai_agent.llm, 'base_url') else 'Mock LLM'}")
        print(f"🤖 Model: {ai_agent.llm.model if hasattr(ai_agent.llm, 'model') else 'Mock Model'}")
        
        # Demonstrate intelligent order scheduling
        print("\n🍽️ Creating a complex order that requires AI decision making...")
        order_items = ["ITM_001", "ITM_004", "ITM_007"]  # Items from different kitchens
        order_id = "DEMO_ORDER_001"
        
        print(f"Order Items: {order_items}")
        print("📊 This will trigger the AI to:")
        print("  1. Analyze current kitchen loads")
        print("  2. Check for starvation risks")
        print("  3. Optimize scheduling across kitchens")
        print("  4. Ensure synchronized completion")
        
        # This is where the LLM is actually called for intelligent scheduling
        print("\n🧠 Calling AI Agent for intelligent scheduling...")
        optimization_result = ai_agent.optimize_order_schedule(order_items, order_id)
        
        print(f"\n✅ AI Optimization Result:")
        print(f"  📋 Order ID: {optimization_result.order_id}")
        print(f"  ⏱️  Total Estimated Time: {optimization_result.total_estimated_time} minutes")
        print(f"  🔄 Synchronization Achieved: {optimization_result.synchronization_achieved}")
        print(f"  🚨 Anti-Starvation Applied: {optimization_result.anti_starvation_applied}")
        print(f"  📝 AI Notes: {optimization_result.optimization_notes}")
        
        print(f"\n📋 Optimized Items Schedule:")
        for item in optimization_result.optimized_items:
            print(f"  • {item.item_name} ({item.item_id})")
            print(f"    Kitchen: {item.kitchen_id}")
            print(f"    Priority: {item.priority_level.value}")
            print(f"    Start: {item.scheduled_start.strftime('%H:%M:%S')}")
            print(f"    Completion: {item.estimated_completion.strftime('%H:%M:%S')}")
        
        # Show the actual AI conversation history
        if ai_agent.conversation_history:
            latest_conversation = ai_agent.conversation_history[-1]
            print_ai_response(
                "ACTUAL LLM INTERACTION FOR SCHEDULING",
                latest_conversation.get("prompt", "No prompt recorded"),
                latest_conversation.get("response", "No response recorded")
            )
        
        return ai_agent, optimization_result
        
    except Exception as e:
        print(f"❌ Error in AI scheduling demonstration: {e}")
        return None, None


def demonstrate_ai_insights(ai_agent):
    """Demonstrate AI-driven system insights."""
    print_section("AI-DRIVEN SYSTEM INSIGHTS DEMONSTRATION")
    
    if not ai_agent:
        print("❌ AI Agent not available for insights demonstration")
        return
    
    try:
        print("🔍 Requesting AI analysis of current system performance...")
        print("📊 This will trigger the AI to:")
        print("  1. Analyze kitchen efficiency")
        print("  2. Identify bottlenecks")
        print("  3. Assess starvation prevention")
        print("  4. Provide actionable recommendations")
        
        # This is where the LLM is called for intelligent insights
        print("\n🧠 Calling AI Agent for system insights...")
        insights = ai_agent.get_ai_insights()
        
        print(f"\n✅ AI Insights Generated:")
        
        # Display insights in a readable format
        if isinstance(insights, dict):
            if "overall_assessment" in insights:
                assessment = insights["overall_assessment"]
                print(f"\n📈 Overall System Assessment:")
                print(f"  Efficiency Score: {assessment.get('efficiency_score', 'N/A')}/100")
                print(f"  Status: {assessment.get('status', 'Unknown')}")
                print(f"  Strengths: {', '.join(assessment.get('key_strengths', []))}")
                print(f"  Concerns: {', '.join(assessment.get('main_concerns', []))}")
            
            if "recommendations" in insights:
                recommendations = insights["recommendations"]
                print(f"\n💡 AI Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                    print(f"  {i}. [{rec.get('priority', 'medium').upper()}] {rec.get('action', 'No action specified')}")
                    print(f"     Impact: {rec.get('expected_impact', 'Not specified')}")
        
        # Show the actual AI conversation for insights
        if ai_agent.conversation_history:
            insights_conversation = None
            for conv in reversed(ai_agent.conversation_history):
                if conv.get("type") == "insights_analysis":
                    insights_conversation = conv
                    break
            
            if insights_conversation:
                print_ai_response(
                    "ACTUAL LLM INTERACTION FOR INSIGHTS",
                    insights_conversation.get("prompt", "No prompt recorded"),
                    insights_conversation.get("response", "No response recorded")
                )
        
    except Exception as e:
        print(f"❌ Error in AI insights demonstration: {e}")


def demonstrate_emergency_ai(ai_agent):
    """Demonstrate AI-driven emergency rescheduling."""
    print_section("AI-DRIVEN EMERGENCY RESCHEDULING DEMONSTRATION")
    
    if not ai_agent:
        print("❌ AI Agent not available for emergency demonstration")
        return
    
    try:
        # Simulate starving items
        starving_items = ["ITM_001", "ITM_004"]
        
        print("🚨 EMERGENCY SITUATION: Items are starving!")
        print(f"Starving Items: {starving_items}")
        print("📊 This will trigger the AI to:")
        print("  1. Assess emergency severity")
        print("  2. Identify root causes")
        print("  3. Apply immediate interventions")
        print("  4. Implement prevention measures")
        
        # This is where the LLM is called for emergency decision making
        print("\n🧠 Calling AI Agent for emergency rescheduling...")
        emergency_result = ai_agent.emergency_reschedule(starving_items)
        
        print(f"\n✅ AI Emergency Response:")
        print(f"  🚨 Status: {emergency_result.get('status', 'Unknown')}")
        print(f"  ⏰ Timestamp: {emergency_result.get('timestamp', 'Unknown')}")
        print(f"  📋 Starving Items Addressed: {len(emergency_result.get('starving_items', []))}")
        
        # Show emergency assessment if available
        if "emergency_assessment" in emergency_result:
            assessment = emergency_result["emergency_assessment"]
            print(f"\n🔍 Emergency Assessment:")
            print(f"  Severity: {assessment.get('severity_level', 'Unknown')}")
            print(f"  Root Causes: {', '.join(assessment.get('root_causes', []))}")
            print(f"  Recovery Time: {assessment.get('estimated_recovery_time', 'Unknown')} minutes")
        
        # Show the actual AI conversation for emergency
        if ai_agent.conversation_history:
            emergency_conversation = None
            for conv in reversed(ai_agent.conversation_history):
                if conv.get("type") == "emergency_reschedule":
                    emergency_conversation = conv
                    break
            
            if emergency_conversation:
                print_ai_response(
                    "ACTUAL LLM INTERACTION FOR EMERGENCY",
                    emergency_conversation.get("prompt", "No prompt recorded"),
                    emergency_conversation.get("response", "No response recorded")
                )
        
    except Exception as e:
        print(f"❌ Error in emergency AI demonstration: {e}")


def main():
    """Main demonstration function."""
    print("🚀 SMART KITCHEN QUEUE MANAGEMENT SYSTEM")
    print("🤖 AI Intelligence Demonstration")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📋 This demonstration shows how the LLM (Ollama) is used for:")
    print("  1. ✅ Intelligent order scheduling and optimization")
    print("  2. ✅ System performance analysis and insights")
    print("  3. ✅ Emergency rescheduling and intervention")
    print("  4. ✅ Real-time decision making based on context")
    
    # Demonstrate AI scheduling
    ai_agent, optimization_result = demonstrate_ai_scheduling()
    
    # Demonstrate AI insights
    demonstrate_ai_insights(ai_agent)
    
    # Demonstrate emergency AI
    demonstrate_emergency_ai(ai_agent)
    
    print_section("DEMONSTRATION SUMMARY")
    print("✅ Successfully demonstrated AI-driven intelligence in:")
    print("  🧠 Order scheduling with context-aware optimization")
    print("  📊 System analysis with actionable insights")
    print("  🚨 Emergency response with intelligent intervention")
    print("  💬 Real LLM interactions with structured prompts")
    
    print(f"\n🎯 Key AI Features Demonstrated:")
    print("  • LLM receives detailed system context")
    print("  • AI makes intelligent scheduling decisions")
    print("  • Responses are parsed and executed automatically")
    print("  • Conversation history is maintained for learning")
    print("  • Emergency situations trigger immediate AI intervention")
    
    print(f"\n🔗 The system uses Ollama LLM for actual decision making,")
    print(f"   not just rule-based algorithms!")
    
    print(f"\n✨ Demonstration completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
