/**
 * Kitchens API Service
 * Handles all kitchen-related API calls
 */

import { apiClient } from '@/lib/api-client';
import {
  CompleteItemRequest,
  KitchenStatusUpdateRequest,
  KitchenStatusResponse,
  KitchenStatusListResponse,
  Kitchen,
  QueueItem,
  KitchenStatus,
  BaseResponse
} from '@/types/api';

export class KitchensApiService {
  private readonly basePath = '/api/kitchens';

  /**
   * Get all kitchens with their current status
   */
  async getKitchens(): Promise<KitchenStatusListResponse> {
    return apiClient.get<KitchenStatusListResponse>(this.basePath);
  }

  /**
   * Get specific kitchen status and queue
   */
  async getKitchenStatus(kitchenId: string): Promise<KitchenStatusResponse> {
    return apiClient.get<KitchenStatusResponse>(`${this.basePath}/${kitchenId}/status`);
  }

  /**
   * Update kitchen status
   */
  async updateKitchenStatus(statusUpdate: KitchenStatusUpdateRequest): Promise<BaseResponse> {
    return apiClient.put<BaseResponse>(
      `${this.basePath}/${statusUpdate.kitchen_id}/status`,
      statusUpdate
    );
  }

  /**
   * Get kitchen queue items
   */
  async getKitchenQueue(kitchenId: string): Promise<QueueItem[]> {
    const response = await apiClient.get<{ queue_items: QueueItem[] }>(
      `${this.basePath}/${kitchenId}/queue`
    );
    return response.queue_items;
  }

  /**
   * Complete a queue item
   */
  async completeItem(completeRequest: CompleteItemRequest): Promise<BaseResponse> {
    return apiClient.post<BaseResponse>(`${this.basePath}/complete-item`, completeRequest);
  }

  /**
   * Get kitchen efficiency metrics
   */
  async getKitchenEfficiency(kitchenId: string, period?: string): Promise<any> {
    const params = period ? `?period=${period}` : '';
    return apiClient.get(`${this.basePath}/${kitchenId}/efficiency${params}`);
  }

  /**
   * Get kitchen load distribution
   */
  async getKitchenLoads(): Promise<Record<string, number>> {
    const response = await apiClient.get<{ kitchen_loads: Record<string, number> }>(
      `${this.basePath}/loads`
    );
    return response.kitchen_loads;
  }

  /**
   * Set kitchen to active status
   */
  async activateKitchen(kitchenId: string): Promise<BaseResponse> {
    return this.updateKitchenStatus({
      kitchen_id: kitchenId,
      status: KitchenStatus.ACTIVE
    });
  }

  /**
   * Set kitchen to maintenance status
   */
  async setKitchenMaintenance(kitchenId: string, notes?: string): Promise<BaseResponse> {
    return this.updateKitchenStatus({
      kitchen_id: kitchenId,
      status: KitchenStatus.MAINTENANCE,
      notes
    });
  }

  /**
   * Set kitchen to offline status
   */
  async setKitchenOffline(kitchenId: string, notes?: string): Promise<BaseResponse> {
    return this.updateKitchenStatus({
      kitchen_id: kitchenId,
      status: KitchenStatus.OFFLINE,
      notes
    });
  }

  /**
   * Get active kitchens only
   */
  async getActiveKitchens(): Promise<Kitchen[]> {
    const response = await this.getKitchens();
    return response.kitchens.filter(kitchen => kitchen.status === KitchenStatus.ACTIVE);
  }

  /**
   * Get kitchen performance summary
   */
  async getKitchenPerformance(kitchenId: string, days: number = 7): Promise<any> {
    return apiClient.get(`${this.basePath}/${kitchenId}/performance?days=${days}`);
  }

  /**
   * Get kitchen staff assignments
   */
  async getKitchenStaff(kitchenId: string): Promise<any> {
    return apiClient.get(`${this.basePath}/${kitchenId}/staff`);
  }

  /**
   * Assign staff to kitchen
   */
  async assignStaff(kitchenId: string, staffId: string): Promise<BaseResponse> {
    return apiClient.post<BaseResponse>(`${this.basePath}/${kitchenId}/staff`, {
      staff_id: staffId
    });
  }

  /**
   * Remove staff from kitchen
   */
  async removeStaff(kitchenId: string, staffId: string): Promise<BaseResponse> {
    return apiClient.delete<BaseResponse>(`${this.basePath}/${kitchenId}/staff/${staffId}`);
  }

  /**
   * Get kitchen capacity utilization
   */
  async getKitchenUtilization(kitchenId: string): Promise<{
    current_load: number;
    capacity: number;
    utilization_percentage: number;
  }> {
    return apiClient.get(`${this.basePath}/${kitchenId}/utilization`);
  }

  /**
   * Emergency stop kitchen operations
   */
  async emergencyStop(kitchenId: string, reason: string): Promise<BaseResponse> {
    return apiClient.post<BaseResponse>(`${this.basePath}/${kitchenId}/emergency-stop`, {
      reason
    });
  }

  /**
   * Resume kitchen operations after emergency stop
   */
  async resumeOperations(kitchenId: string): Promise<BaseResponse> {
    return apiClient.post<BaseResponse>(`${this.basePath}/${kitchenId}/resume`);
  }
}

// Export singleton instance
export const kitchensApi = new KitchensApiService();
