/**
 * Real-time API Service
 * Handles real-time monitoring and performance endpoints
 */

import { apiClient } from '@/lib/api-client';
import {
  QueueStatusResponse,
  PerformanceMetricsResponse,
  PerformanceQueryRequest,
  PerformanceHistoryResponse,
  QueueItem
} from '@/types/api';

export class RealtimeApiService {
  private readonly basePath = '/api/realtime';

  /**
   * Get current queue status across all kitchens
   */
  async getQueueStatus(): Promise<QueueStatusResponse> {
    return apiClient.get<QueueStatusResponse>(`${this.basePath}/queue-status`);
  }

  /**
   * Get real-time performance metrics
   */
  async getPerformanceMetrics(period?: string): Promise<PerformanceMetricsResponse> {
    const params = period ? `?period=${period}` : '';
    return apiClient.get<PerformanceMetricsResponse>(`${this.basePath}/performance${params}`);
  }

  /**
   * Get performance history with filtering
   */
  async getPerformanceHistory(query: PerformanceQueryRequest): Promise<PerformanceHistoryResponse> {
    return apiClient.post<PerformanceHistoryResponse>(`${this.basePath}/performance/history`, query);
  }

  /**
   * Get current system load
   */
  async getSystemLoad(): Promise<{
    total_orders: number;
    active_kitchens: number;
    average_wait_time: number;
    system_efficiency: number;
  }> {
    return apiClient.get(`${this.basePath}/system-load`);
  }

  /**
   * Get bottleneck analysis
   */
  async getBottlenecks(): Promise<{
    bottlenecks: Array<{
      kitchen_id: string;
      severity: string;
      description: string;
      suggested_action: string;
    }>;
  }> {
    return apiClient.get(`${this.basePath}/bottlenecks`);
  }

  /**
   * Get starvation alerts
   */
  async getStarvationAlerts(): Promise<{
    alerts: Array<{
      queue_id: string;
      order_id: string;
      item_id: string;
      starvation_count: number;
      wait_time_minutes: number;
      priority_level: string;
    }>;
  }> {
    return apiClient.get(`${this.basePath}/starvation-alerts`);
  }

  /**
   * Get real-time kitchen loads
   */
  async getKitchenLoads(): Promise<Record<string, {
    current_load: number;
    capacity: number;
    utilization: number;
    queue_length: number;
  }>> {
    return apiClient.get(`${this.basePath}/kitchen-loads`);
  }

  /**
   * Get efficiency trends
   */
  async getEfficiencyTrends(days: number = 7): Promise<{
    trends: Array<{
      date: string;
      overall_efficiency: number;
      kitchen_efficiencies: Record<string, number>;
      order_completion_rate: number;
    }>;
  }> {
    return apiClient.get(`${this.basePath}/efficiency-trends?days=${days}`);
  }

  /**
   * Get wait time statistics
   */
  async getWaitTimeStats(): Promise<{
    average_wait_time: number;
    median_wait_time: number;
    max_wait_time: number;
    wait_time_by_kitchen: Record<string, number>;
  }> {
    return apiClient.get(`${this.basePath}/wait-time-stats`);
  }

  /**
   * Get order completion predictions
   */
  async getCompletionPredictions(): Promise<{
    predictions: Array<{
      order_id: string;
      estimated_completion: string;
      confidence: number;
      factors: string[];
    }>;
  }> {
    return apiClient.get(`${this.basePath}/completion-predictions`);
  }

  /**
   * Get high-priority items that need attention
   */
  async getHighPriorityItems(): Promise<QueueItem[]> {
    const response = await apiClient.get<{ items: QueueItem[] }>(`${this.basePath}/high-priority`);
    return response.items;
  }

  /**
   * Get performance summary for dashboard
   */
  async getDashboardSummary(): Promise<{
    total_orders_today: number;
    completed_orders_today: number;
    average_completion_time: number;
    active_kitchens: number;
    current_queue_length: number;
    efficiency_score: number;
    alerts_count: number;
  }> {
    return apiClient.get(`${this.basePath}/dashboard-summary`);
  }

  /**
   * Get real-time order flow
   */
  async getOrderFlow(): Promise<{
    orders_per_hour: Array<{
      hour: string;
      count: number;
    }>;
    peak_hours: string[];
    current_rate: number;
  }> {
    return apiClient.get(`${this.basePath}/order-flow`);
  }

  /**
   * Get kitchen performance comparison
   */
  async getKitchenComparison(): Promise<{
    kitchens: Array<{
      kitchen_id: string;
      name: string;
      efficiency: number;
      throughput: number;
      average_prep_time: number;
      error_rate: number;
    }>;
  }> {
    return apiClient.get(`${this.basePath}/kitchen-comparison`);
  }

  /**
   * Get system health indicators
   */
  async getHealthIndicators(): Promise<{
    overall_health: 'healthy' | 'warning' | 'critical';
    indicators: Array<{
      name: string;
      status: 'good' | 'warning' | 'critical';
      value: number;
      threshold: number;
      description: string;
    }>;
  }> {
    return apiClient.get(`${this.basePath}/health-indicators`);
  }
}

// Export singleton instance
export const realtimeApi = new RealtimeApiService();
