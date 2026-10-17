/**
 * React hooks for Real-time API
 * Provides React Query integration for real-time monitoring
 */

import { useQuery } from '@tanstack/react-query';
import { 
  realtimeApi, 
  PerformanceQueryRequest 
} from '@/services/api';

// Query keys
export const realtimeKeys = {
  all: ['realtime'] as const,
  queueStatus: () => [...realtimeKeys.all, 'queue-status'] as const,
  performance: (period?: string) => [...realtimeKeys.all, 'performance', period] as const,
  performanceHistory: (query: PerformanceQueryRequest) => [...realtimeKeys.all, 'performance-history', query] as const,
  systemLoad: () => [...realtimeKeys.all, 'system-load'] as const,
  bottlenecks: () => [...realtimeKeys.all, 'bottlenecks'] as const,
  starvationAlerts: () => [...realtimeKeys.all, 'starvation-alerts'] as const,
  kitchenLoads: () => [...realtimeKeys.all, 'kitchen-loads'] as const,
  efficiencyTrends: (days: number) => [...realtimeKeys.all, 'efficiency-trends', days] as const,
  waitTimeStats: () => [...realtimeKeys.all, 'wait-time-stats'] as const,
  completionPredictions: () => [...realtimeKeys.all, 'completion-predictions'] as const,
  highPriorityItems: () => [...realtimeKeys.all, 'high-priority-items'] as const,
  dashboardSummary: () => [...realtimeKeys.all, 'dashboard-summary'] as const,
  orderFlow: () => [...realtimeKeys.all, 'order-flow'] as const,
  kitchenComparison: () => [...realtimeKeys.all, 'kitchen-comparison'] as const,
  healthIndicators: () => [...realtimeKeys.all, 'health-indicators'] as const,
};

/**
 * Hook to fetch current queue status
 */
export const useQueueStatus = () => {
  return useQuery({
    queryKey: realtimeKeys.queueStatus(),
    queryFn: () => realtimeApi.getQueueStatus(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 15000, // Refetch every 15 seconds
  });
};

/**
 * Hook to fetch real-time performance metrics
 */
export const usePerformanceMetrics = (period?: string) => {
  return useQuery({
    queryKey: realtimeKeys.performance(period),
    queryFn: () => realtimeApi.getPerformanceMetrics(period),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch performance history
 */
export const usePerformanceHistory = (query: PerformanceQueryRequest) => {
  return useQuery({
    queryKey: realtimeKeys.performanceHistory(query),
    queryFn: () => realtimeApi.getPerformanceHistory(query),
    staleTime: 300000, // 5 minutes
    enabled: !!(query.start_date || query.end_date || query.kitchen_id || query.item_id),
  });
};

/**
 * Hook to fetch current system load
 */
export const useSystemLoad = () => {
  return useQuery({
    queryKey: realtimeKeys.systemLoad(),
    queryFn: () => realtimeApi.getSystemLoad(),
    staleTime: 15000, // 15 seconds
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

/**
 * Hook to fetch bottleneck analysis
 */
export const useBottlenecks = () => {
  return useQuery({
    queryKey: realtimeKeys.bottlenecks(),
    queryFn: () => realtimeApi.getBottlenecks(),
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refetch every 2 minutes
  });
};

/**
 * Hook to fetch starvation alerts
 */
export const useStarvationAlerts = () => {
  return useQuery({
    queryKey: realtimeKeys.starvationAlerts(),
    queryFn: () => realtimeApi.getStarvationAlerts(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 20000, // Refetch every 20 seconds
  });
};

/**
 * Hook to fetch real-time kitchen loads
 */
export const useRealtimeKitchenLoads = () => {
  return useQuery({
    queryKey: realtimeKeys.kitchenLoads(),
    queryFn: () => realtimeApi.getKitchenLoads(),
    staleTime: 15000, // 15 seconds
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

/**
 * Hook to fetch efficiency trends
 */
export const useEfficiencyTrends = (days: number = 7) => {
  return useQuery({
    queryKey: realtimeKeys.efficiencyTrends(days),
    queryFn: () => realtimeApi.getEfficiencyTrends(days),
    staleTime: 600000, // 10 minutes
    refetchInterval: 1800000, // Refetch every 30 minutes
  });
};

/**
 * Hook to fetch wait time statistics
 */
export const useWaitTimeStats = () => {
  return useQuery({
    queryKey: realtimeKeys.waitTimeStats(),
    queryFn: () => realtimeApi.getWaitTimeStats(),
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refetch every 2 minutes
  });
};

/**
 * Hook to fetch order completion predictions
 */
export const useCompletionPredictions = () => {
  return useQuery({
    queryKey: realtimeKeys.completionPredictions(),
    queryFn: () => realtimeApi.getCompletionPredictions(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch high-priority items
 */
export const useHighPriorityItems = () => {
  return useQuery({
    queryKey: realtimeKeys.highPriorityItems(),
    queryFn: () => realtimeApi.getHighPriorityItems(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 15000, // Refetch every 15 seconds
  });
};

/**
 * Hook to fetch dashboard summary
 */
export const useDashboardSummary = () => {
  return useQuery({
    queryKey: realtimeKeys.dashboardSummary(),
    queryFn: () => realtimeApi.getDashboardSummary(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch real-time order flow
 */
export const useOrderFlow = () => {
  return useQuery({
    queryKey: realtimeKeys.orderFlow(),
    queryFn: () => realtimeApi.getOrderFlow(),
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refetch every 2 minutes
  });
};

/**
 * Hook to fetch kitchen performance comparison
 */
export const useKitchenComparison = () => {
  return useQuery({
    queryKey: realtimeKeys.kitchenComparison(),
    queryFn: () => realtimeApi.getKitchenComparison(),
    staleTime: 300000, // 5 minutes
    refetchInterval: 600000, // Refetch every 10 minutes
  });
};

/**
 * Hook to fetch system health indicators
 */
export const useHealthIndicators = () => {
  return useQuery({
    queryKey: realtimeKeys.healthIndicators(),
    queryFn: () => realtimeApi.getHealthIndicators(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook for real-time dashboard data (combines multiple queries)
 */
export const useDashboardData = () => {
  const dashboardSummary = useDashboardSummary();
  const queueStatus = useQueueStatus();
  const systemLoad = useSystemLoad();
  const starvationAlerts = useStarvationAlerts();
  const healthIndicators = useHealthIndicators();

  return {
    summary: dashboardSummary,
    queue: queueStatus,
    load: systemLoad,
    alerts: starvationAlerts,
    health: healthIndicators,
    isLoading: dashboardSummary.isLoading || queueStatus.isLoading || systemLoad.isLoading,
    isError: dashboardSummary.isError || queueStatus.isError || systemLoad.isError,
    refetch: () => {
      dashboardSummary.refetch();
      queueStatus.refetch();
      systemLoad.refetch();
      starvationAlerts.refetch();
      healthIndicators.refetch();
    },
  };
};

/**
 * Hook for analytics data (combines multiple queries)
 */
export const useAnalyticsData = (days: number = 7) => {
  const efficiencyTrends = useEfficiencyTrends(days);
  const waitTimeStats = useWaitTimeStats();
  const kitchenComparison = useKitchenComparison();
  const bottlenecks = useBottlenecks();

  return {
    trends: efficiencyTrends,
    waitTimes: waitTimeStats,
    comparison: kitchenComparison,
    bottlenecks: bottlenecks,
    isLoading: efficiencyTrends.isLoading || waitTimeStats.isLoading || kitchenComparison.isLoading,
    isError: efficiencyTrends.isError || waitTimeStats.isError || kitchenComparison.isError,
    refetch: () => {
      efficiencyTrends.refetch();
      waitTimeStats.refetch();
      kitchenComparison.refetch();
      bottlenecks.refetch();
    },
  };
};
