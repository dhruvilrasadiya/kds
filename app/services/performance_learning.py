"""
Performance Learning System for the Smart Kitchen Queue Management System.
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

from app.services.excel_service import ExcelDataService
from app.models import PerformanceRecord, PriorityLevel
from app.config import config

logger = logging.getLogger(__name__)


class PerformanceLearning:
    """System for learning from historical performance and improving estimates."""
    
    def __init__(self, excel_service: ExcelDataService):
        """Initialize the performance learning system."""
        self.excel_service = excel_service
        self._performance_cache = {}
        self._learning_insights = {}
        self._last_update = None
        
        logger.info("Performance Learning System initialized")
    
    def record_completion(self, item_id: str, kitchen_id: str, order_id: str,
                         actual_time: int, scheduled_time: int, 
                         priority_level: PriorityLevel = PriorityLevel.NORMAL,
                         kitchen_load: int = 0, starvation_count: int = 0):
        """Record actual completion time vs scheduled time."""
        try:
            delay_minutes = max(0, actual_time - scheduled_time)
            
            performance_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'kitchen_id': kitchen_id,
                'item_id': item_id,
                'order_id': order_id,
                'actual_prep_time': actual_time,
                'scheduled_prep_time': scheduled_time,
                'delay_minutes': delay_minutes,
                'kitchen_load': kitchen_load,
                'priority_level': priority_level.value,
                'starvation_count': starvation_count
            }
            
            # Update Excel with new performance data
            self.excel_service.update_historical_performance(performance_data)
            
            # Clear cache to force reload
            self._performance_cache.clear()
            self._last_update = datetime.now()
            
            logger.info(f"Recorded completion for {item_id}: {actual_time}min (scheduled: {scheduled_time}min)")
            
        except Exception as e:
            logger.error(f"Error recording completion for {item_id}: {e}")
    
    def analyze_kitchen_efficiency(self, kitchen_id: str, days_back: int = 30) -> Dict:
        """Analyze kitchen performance patterns and efficiency."""
        try:
            historical_data = self.excel_service.load_historical_data()
            
            # Filter data for specific kitchen and time period
            cutoff_date = datetime.now() - timedelta(days=days_back)
            kitchen_data = historical_data[
                (historical_data['kitchen_id'] == kitchen_id) &
                (historical_data['date'] >= cutoff_date)
            ]
            
            if kitchen_data.empty:
                return {"error": f"No data found for kitchen {kitchen_id}"}
            
            # Calculate efficiency metrics
            total_items = len(kitchen_data)
            avg_actual_time = kitchen_data['actual_prep_time'].mean()
            avg_scheduled_time = kitchen_data['scheduled_prep_time'].mean()
            avg_delay = kitchen_data['delay_minutes'].mean()
            
            # Efficiency ratio (scheduled/actual - higher is better)
            efficiency_ratio = avg_scheduled_time / avg_actual_time if avg_actual_time > 0 else 0
            
            # On-time performance (percentage of items completed without delay)
            on_time_items = len(kitchen_data[kitchen_data['delay_minutes'] == 0])
            on_time_percentage = (on_time_items / total_items * 100) if total_items > 0 else 0
            
            # Load impact analysis
            load_impact = kitchen_data.groupby('kitchen_load').agg({
                'actual_prep_time': 'mean',
                'delay_minutes': 'mean'
            }).to_dict()
            
            # Priority impact analysis
            priority_impact = kitchen_data.groupby('priority_level').agg({
                'actual_prep_time': 'mean',
                'delay_minutes': 'mean'
            }).to_dict()
            
            # Time-based patterns (hourly performance)
            kitchen_data['hour'] = pd.to_datetime(kitchen_data['date']).dt.hour
            hourly_performance = kitchen_data.groupby('hour').agg({
                'actual_prep_time': 'mean',
                'delay_minutes': 'mean'
            }).to_dict()
            
            analysis = {
                "kitchen_id": kitchen_id,
                "analysis_period_days": days_back,
                "total_items_analyzed": total_items,
                "efficiency_metrics": {
                    "avg_actual_time": round(avg_actual_time, 2),
                    "avg_scheduled_time": round(avg_scheduled_time, 2),
                    "avg_delay_minutes": round(avg_delay, 2),
                    "efficiency_ratio": round(efficiency_ratio, 3),
                    "on_time_percentage": round(on_time_percentage, 2)
                },
                "load_impact": load_impact,
                "priority_impact": priority_impact,
                "hourly_performance": hourly_performance,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Cache the analysis
            self._performance_cache[f"kitchen_efficiency_{kitchen_id}"] = analysis
            
            logger.info(f"Kitchen efficiency analysis completed for {kitchen_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing kitchen efficiency for {kitchen_id}: {e}")
            return {"error": str(e)}
    
    def update_prep_time_estimates(self) -> Dict[str, float]:
        """Update preparation time estimates based on historical data."""
        try:
            historical_data = self.excel_service.load_historical_data()
            
            # Filter recent data (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=config.PERFORMANCE_HISTORY_DAYS)
            recent_data = historical_data[historical_data['date'] >= cutoff_date]
            
            # Calculate updated estimates for each item
            updated_estimates = {}
            
            for item_id in recent_data['item_id'].unique():
                item_data = recent_data[recent_data['item_id'] == item_id]
                
                if len(item_data) >= 3:  # Need at least 3 data points
                    # Use weighted average (more recent data has higher weight)
                    weights = np.exp(np.linspace(-1, 0, len(item_data)))
                    weighted_avg = np.average(item_data['actual_prep_time'], weights=weights)
                    
                    # Apply confidence factor based on data consistency
                    std_dev = item_data['actual_prep_time'].std()
                    confidence = max(0.5, 1 - (std_dev / weighted_avg)) if weighted_avg > 0 else 0.5
                    
                    updated_estimates[item_id] = {
                        "estimated_prep_time": round(weighted_avg, 1),
                        "confidence": round(confidence, 3),
                        "data_points": len(item_data),
                        "std_deviation": round(std_dev, 2)
                    }
            
            logger.info(f"Updated prep time estimates for {len(updated_estimates)} items")
            return updated_estimates
            
        except Exception as e:
            logger.error(f"Error updating prep time estimates: {e}")
            return {}
    
    def identify_bottlenecks(self) -> List[Dict]:
        """Identify system bottlenecks and performance issues."""
        try:
            historical_data = self.excel_service.load_historical_data()
            
            # Filter recent data
            cutoff_date = datetime.now() - timedelta(days=7)  # Last week
            recent_data = historical_data[historical_data['date'] >= cutoff_date]
            
            bottlenecks = []
            
            # Kitchen-level bottlenecks
            kitchen_performance = recent_data.groupby('kitchen_id').agg({
                'delay_minutes': ['mean', 'count'],
                'actual_prep_time': 'mean'
            }).round(2)
            
            for kitchen_id in kitchen_performance.index:
                avg_delay = kitchen_performance.loc[kitchen_id, ('delay_minutes', 'mean')]
                item_count = kitchen_performance.loc[kitchen_id, ('delay_minutes', 'count')]
                
                if avg_delay > 5 and item_count > 10:  # Significant delays with enough data
                    bottlenecks.append({
                        "type": "kitchen_bottleneck",
                        "kitchen_id": kitchen_id,
                        "avg_delay_minutes": avg_delay,
                        "items_processed": item_count,
                        "severity": "high" if avg_delay > 10 else "medium"
                    })
            
            # Item-level bottlenecks
            item_performance = recent_data.groupby('item_id').agg({
                'delay_minutes': ['mean', 'count'],
                'actual_prep_time': 'mean'
            }).round(2)
            
            for item_id in item_performance.index:
                avg_delay = item_performance.loc[item_id, ('delay_minutes', 'mean')]
                item_count = item_performance.loc[item_id, ('delay_minutes', 'count')]
                
                if avg_delay > 8 and item_count > 5:  # Consistently delayed items
                    bottlenecks.append({
                        "type": "item_bottleneck",
                        "item_id": item_id,
                        "avg_delay_minutes": avg_delay,
                        "occurrences": item_count,
                        "severity": "high" if avg_delay > 15 else "medium"
                    })
            
            # Load-based bottlenecks
            load_performance = recent_data.groupby('kitchen_load').agg({
                'delay_minutes': 'mean',
                'actual_prep_time': 'mean'
            }).round(2)
            
            for load_level in load_performance.index:
                if load_level > 2:  # High load situations
                    avg_delay = load_performance.loc[load_level, 'delay_minutes']
                    if avg_delay > 7:
                        bottlenecks.append({
                            "type": "load_bottleneck",
                            "load_level": load_level,
                            "avg_delay_minutes": avg_delay,
                            "severity": "high" if avg_delay > 12 else "medium"
                        })
            
            logger.info(f"Identified {len(bottlenecks)} bottlenecks")
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {e}")
            return []

    def get_predictive_insights(self, kitchen_id: str, hour: int) -> Dict:
        """Get predictive insights for kitchen performance at specific hour."""
        try:
            historical_data = self.excel_service.load_historical_data()
            load_patterns = self.excel_service.load_kitchen_load_patterns()

            # Filter data for specific kitchen and hour
            historical_data['hour'] = pd.to_datetime(historical_data['date']).dt.hour
            hour_data = historical_data[
                (historical_data['kitchen_id'] == kitchen_id) &
                (historical_data['hour'] == hour)
            ]

            # Get expected load from patterns
            pattern_col = f"kitchen_{kitchen_id.split('_')[1].lower()}_avg_load"
            expected_load = 0
            if pattern_col in load_patterns.columns:
                pattern_row = load_patterns[load_patterns['hour'] == hour]
                if not pattern_row.empty:
                    expected_load = pattern_row[pattern_col].iloc[0]

            insights = {
                "kitchen_id": kitchen_id,
                "hour": hour,
                "expected_load": expected_load,
                "historical_performance": {},
                "recommendations": []
            }

            if not hour_data.empty:
                insights["historical_performance"] = {
                    "avg_prep_time": round(hour_data['actual_prep_time'].mean(), 2),
                    "avg_delay": round(hour_data['delay_minutes'].mean(), 2),
                    "total_items": len(hour_data),
                    "on_time_percentage": round(
                        len(hour_data[hour_data['delay_minutes'] == 0]) / len(hour_data) * 100, 2
                    )
                }

                # Generate recommendations
                avg_delay = insights["historical_performance"]["avg_delay"]
                if avg_delay > 5:
                    insights["recommendations"].append(
                        f"High delays expected at {hour}:00 - consider pre-preparation"
                    )

                if expected_load > 2:
                    insights["recommendations"].append(
                        f"High load expected ({expected_load}) - ensure adequate staffing"
                    )

            return insights

        except Exception as e:
            logger.error(f"Error getting predictive insights: {e}")
            return {"error": str(e)}

    def generate_learning_report(self) -> Dict:
        """Generate comprehensive learning report."""
        try:
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "system_performance": {},
                "kitchen_analysis": {},
                "bottlenecks": [],
                "recommendations": [],
                "learning_insights": {}
            }

            # Overall system performance
            historical_data = self.excel_service.load_historical_data()
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_data = historical_data[historical_data['date'] >= cutoff_date]

            if not recent_data.empty:
                report["system_performance"] = {
                    "total_items_processed": len(recent_data),
                    "avg_prep_time": round(recent_data['actual_prep_time'].mean(), 2),
                    "avg_delay": round(recent_data['delay_minutes'].mean(), 2),
                    "overall_efficiency": round(
                        recent_data['scheduled_prep_time'].sum() /
                        recent_data['actual_prep_time'].sum(), 3
                    ) if recent_data['actual_prep_time'].sum() > 0 else 0
                }

            # Kitchen-specific analysis
            kitchens = recent_data['kitchen_id'].unique()
            for kitchen_id in kitchens:
                report["kitchen_analysis"][kitchen_id] = self.analyze_kitchen_efficiency(kitchen_id, 7)

            # Bottlenecks
            report["bottlenecks"] = self.identify_bottlenecks()

            # Updated estimates
            updated_estimates = self.update_prep_time_estimates()
            report["learning_insights"]["updated_estimates_count"] = len(updated_estimates)

            # Generate recommendations
            if report["system_performance"].get("avg_delay", 0) > 5:
                report["recommendations"].append(
                    "System-wide delays detected - review kitchen capacities and scheduling"
                )

            high_severity_bottlenecks = [
                b for b in report["bottlenecks"] if b.get("severity") == "high"
            ]
            if high_severity_bottlenecks:
                report["recommendations"].append(
                    f"{len(high_severity_bottlenecks)} high-severity bottlenecks identified - immediate attention required"
                )

            logger.info("Learning report generated successfully")
            return report

        except Exception as e:
            logger.error(f"Error generating learning report: {e}")
            return {"error": str(e)}

    def optimize_kitchen_capacity_recommendations(self) -> Dict[str, Dict]:
        """Provide capacity optimization recommendations for each kitchen."""
        try:
            recommendations = {}
            historical_data = self.excel_service.load_historical_data()

            # Analyze last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_data = historical_data[historical_data['date'] >= cutoff_date]

            for kitchen_id in recent_data['kitchen_id'].unique():
                kitchen_data = recent_data[recent_data['kitchen_id'] == kitchen_id]

                # Analyze load patterns
                load_analysis = kitchen_data.groupby('kitchen_load').agg({
                    'delay_minutes': ['mean', 'count'],
                    'actual_prep_time': 'mean'
                })

                # Find optimal load level (where delays start increasing significantly)
                optimal_load = 1
                for load in sorted(load_analysis.index):
                    avg_delay = load_analysis.loc[load, ('delay_minutes', 'mean')]
                    if avg_delay > 3:  # Threshold for acceptable delay
                        break
                    optimal_load = load

                # Current kitchen config
                kitchen_config = self.excel_service.get_kitchen_by_id(kitchen_id)
                current_capacity = kitchen_config['capacity'] if kitchen_config else 3

                recommendations[kitchen_id] = {
                    "current_capacity": current_capacity,
                    "optimal_load_level": optimal_load,
                    "capacity_recommendation": max(optimal_load + 1, current_capacity),
                    "utilization_analysis": {
                        "avg_load": round(kitchen_data['kitchen_load'].mean(), 2),
                        "max_load_observed": int(kitchen_data['kitchen_load'].max()),
                        "load_efficiency": load_analysis.to_dict()
                    },
                    "performance_at_capacity": {
                        "avg_delay_at_max": round(
                            kitchen_data[kitchen_data['kitchen_load'] == kitchen_data['kitchen_load'].max()]['delay_minutes'].mean(), 2
                        ) if not kitchen_data.empty else 0
                    }
                }

            logger.info(f"Generated capacity recommendations for {len(recommendations)} kitchens")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating capacity recommendations: {e}")
            return {}

    def clear_cache(self):
        """Clear performance cache to force fresh analysis."""
        self._performance_cache.clear()
        logger.info("Performance learning cache cleared")
