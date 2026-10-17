/**
 * Central API Service
 * Combines all API services and provides a unified interface
 */

import { ordersApi, OrdersApiService } from './orders-api';
import { kitchensApi, KitchensApiService } from './kitchens-api';
import { realtimeApi, RealtimeApiService } from './realtime-api';
import { systemApi, SystemApiService } from './system-api';
import { menuApi, MenuApiService } from './menu-api';
import { apiClient, ApiClient } from '@/lib/api-client';

export class ApiService {
  public readonly orders: OrdersApiService;
  public readonly kitchens: KitchensApiService;
  public readonly realtime: RealtimeApiService;
  public readonly system: SystemApiService;
  public readonly menu: MenuApiService;
  public readonly client: ApiClient;

  constructor() {
    this.orders = ordersApi;
    this.kitchens = kitchensApi;
    this.realtime = realtimeApi;
    this.system = systemApi;
    this.menu = menuApi;
    this.client = apiClient;
  }

  /**
   * Test API connectivity
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.client.healthCheck();
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }

  /**
   * Initialize API service
   */
  async initialize(): Promise<void> {
    try {
      // Test connection
      const isConnected = await this.testConnection();
      if (!isConnected) {
        throw new Error('Failed to connect to API server');
      }

      // Get system health
      const health = await this.system.getHealth();
      console.log('API Service initialized successfully:', health);
    } catch (error) {
      console.error('Failed to initialize API service:', error);
      throw error;
    }
  }

  /**
   * Update API base URL
   */
  updateBaseURL(baseURL: string): void {
    this.client.updateBaseURL(baseURL);
  }

  /**
   * Get API configuration
   */
  getConfig() {
    return this.client.getConfig();
  }
}

// Create and export singleton instance
export const api = new ApiService();

// Export individual services for direct access
export {
  ordersApi,
  kitchensApi,
  realtimeApi,
  systemApi,
  menuApi,
  apiClient
};

// Export service classes for custom instances
export {
  OrdersApiService,
  KitchensApiService,
  RealtimeApiService,
  SystemApiService,
  MenuApiService,
  ApiClient
};

// Export utility functions
export {
  isApiError,
  getErrorMessage,
  isSuccessResponse
} from '@/lib/api-client';

// Export types
export * from '@/types/api';
