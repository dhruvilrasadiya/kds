/**
 * System API Service
 * Handles system management, configuration, and health endpoints
 */

import { apiClient } from '@/lib/api-client';
import {
  SystemHealthResponse,
  BaseResponse
} from '@/types/api';

export class SystemApiService {
  private readonly basePath = '/api/system';

  /**
   * Get comprehensive system health check
   */
  async getHealth(): Promise<SystemHealthResponse> {
    return apiClient.get<SystemHealthResponse>(`${this.basePath}/health`);
  }

  /**
   * Get system metrics
   */
  async getMetrics(): Promise<{
    success: boolean;
    message: string;
    metrics: {
      kitchen_metrics: Record<string, any>;
      starvation_metrics: Record<string, any>;
      bottlenecks: any[];
      system_resources: {
        cpu_percent: number;
        memory_percent: number;
        disk_usage: number;
      };
      uptime: string;
    };
    timestamp: string;
  }> {
    return apiClient.get(`${this.basePath}/metrics`);
  }

  /**
   * Get learning report
   */
  async getLearningReport(): Promise<{
    success: boolean;
    message: string;
    report: any;
    timestamp: string;
  }> {
    return apiClient.get(`${this.basePath}/learning-report`);
  }

  /**
   * Reload system configuration
   */
  async reloadConfig(): Promise<BaseResponse> {
    return apiClient.post<BaseResponse>(`${this.basePath}/reload-config`);
  }

  /**
   * Get current system configuration
   */
  async getConfig(): Promise<{
    success: boolean;
    message: string;
    config: {
      excel_file_path: string;
      ollama_base_url: string;
      ollama_model: string;
      max_starvation_count: number;
      synchronization_window_minutes: number;
      performance_history_days: number;
      api_host: string;
      api_port: number;
      debug_mode: boolean;
    };
    timestamp: string;
  }> {
    return apiClient.get(`${this.basePath}/config`);
  }

  /**
   * Update system configuration
   */
  async updateConfig(config: Partial<{
    max_starvation_count: number;
    synchronization_window_minutes: number;
    performance_history_days: number;
    debug_mode: boolean;
  }>): Promise<BaseResponse> {
    return apiClient.put<BaseResponse>(`${this.basePath}/config`, config);
  }

  /**
   * Get system logs
   */
  async getLogs(params?: {
    level?: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
    limit?: number;
    since?: string;
  }): Promise<{
    logs: Array<{
      timestamp: string;
      level: string;
      message: string;
      module: string;
    }>;
    total_count: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.level) queryParams.append('level', params.level);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.since) queryParams.append('since', params.since);

    const url = queryParams.toString() ? `${this.basePath}/logs?${queryParams}` : `${this.basePath}/logs`;
    return apiClient.get(url);
  }

  /**
   * Clear system logs
   */
  async clearLogs(): Promise<BaseResponse> {
    return apiClient.delete<BaseResponse>(`${this.basePath}/logs`);
  }

  /**
   * Get system statistics
   */
  async getStatistics(): Promise<{
    total_orders_processed: number;
    total_items_completed: number;
    average_order_time: number;
    system_uptime: string;
    peak_concurrent_orders: number;
    efficiency_score: number;
    error_rate: number;
  }> {
    return apiClient.get(`${this.basePath}/statistics`);
  }

  /**
   * Export system data
   */
  async exportData(format: 'json' | 'csv' | 'excel' = 'json'): Promise<Blob> {
    const response = await apiClient.get(`${this.basePath}/export?format=${format}`, {
      responseType: 'blob'
    });
    return response;
  }

  /**
   * Import system data
   */
  async importData(file: File): Promise<BaseResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post<BaseResponse>(`${this.basePath}/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Backup system data
   */
  async createBackup(): Promise<{
    success: boolean;
    message: string;
    backup_id: string;
    backup_path: string;
    timestamp: string;
  }> {
    return apiClient.post(`${this.basePath}/backup`);
  }

  /**
   * Restore from backup
   */
  async restoreBackup(backupId: string): Promise<BaseResponse> {
    return apiClient.post<BaseResponse>(`${this.basePath}/restore/${backupId}`);
  }

  /**
   * Get available backups
   */
  async getBackups(): Promise<{
    backups: Array<{
      id: string;
      created_at: string;
      size: number;
      description?: string;
    }>;
  }> {
    return apiClient.get(`${this.basePath}/backups`);
  }

  /**
   * Delete backup
   */
  async deleteBackup(backupId: string): Promise<BaseResponse> {
    return apiClient.delete<BaseResponse>(`${this.basePath}/backups/${backupId}`);
  }

  /**
   * Test system connectivity
   */
  async testConnectivity(): Promise<{
    database: boolean;
    ollama: boolean;
    excel_file: boolean;
    external_apis: boolean;
  }> {
    return apiClient.get(`${this.basePath}/test-connectivity`);
  }

  /**
   * Get system version info
   */
  async getVersion(): Promise<{
    version: string;
    build_date: string;
    git_commit?: string;
    environment: string;
  }> {
    return apiClient.get(`${this.basePath}/version`);
  }
}

// Export singleton instance
export const systemApi = new SystemApiService();
