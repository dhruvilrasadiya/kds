/**
 * Orders API Service
 * Handles all order-related API calls
 */

import { apiClient } from '@/lib/api-client';
import {
  CreateOrderRequest,
  UpdateOrderRequest,
  OrderResponse,
  OrderListResponse,
  Order,
  OrderStatus
} from '@/types/api';

export class OrdersApiService {
  private readonly basePath = '/api/orders';

  /**
   * Create a new order
   */
  async createOrder(orderData: CreateOrderRequest): Promise<OrderResponse> {
    return apiClient.post<OrderResponse>(this.basePath, orderData);
  }

  /**
   * Get all orders with optional filtering
   */
  async getOrders(params?: {
    status?: OrderStatus;
    customer_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<OrderListResponse> {
    const queryParams = new URLSearchParams();
    
    if (params?.status) queryParams.append('status', params.status);
    if (params?.customer_id) queryParams.append('customer_id', params.customer_id);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const url = queryParams.toString() ? `${this.basePath}?${queryParams}` : this.basePath;
    return apiClient.get<OrderListResponse>(url);
  }

  /**
   * Get a specific order by ID
   */
  async getOrder(orderId: string): Promise<OrderResponse> {
    return apiClient.get<OrderResponse>(`${this.basePath}/${orderId}`);
  }

  /**
   * Update an existing order
   */
  async updateOrder(orderId: string, updateData: UpdateOrderRequest): Promise<OrderResponse> {
    return apiClient.put<OrderResponse>(`${this.basePath}/${orderId}`, updateData);
  }

  /**
   * Cancel an order
   */
  async cancelOrder(orderId: string, reason?: string): Promise<OrderResponse> {
    return apiClient.delete<OrderResponse>(`${this.basePath}/${orderId}`, {
      data: { reason }
    });
  }

  /**
   * Get order status history
   */
  async getOrderHistory(orderId: string): Promise<any> {
    return apiClient.get(`${this.basePath}/${orderId}/history`);
  }

  /**
   * Get orders by status (convenience method)
   */
  async getOrdersByStatus(status: OrderStatus): Promise<Order[]> {
    const response = await this.getOrders({ status });
    return response.orders;
  }

  /**
   * Get pending orders
   */
  async getPendingOrders(): Promise<Order[]> {
    return this.getOrdersByStatus(OrderStatus.PENDING);
  }

  /**
   * Get active orders (preparing, cooking, ready)
   */
  async getActiveOrders(): Promise<Order[]> {
    const [preparing, cooking, ready] = await Promise.all([
      this.getOrdersByStatus(OrderStatus.PREPARING),
      this.getOrdersByStatus(OrderStatus.COOKING),
      this.getOrdersByStatus(OrderStatus.READY)
    ]);
    
    return [...preparing, ...cooking, ...ready];
  }

  /**
   * Get completed orders
   */
  async getCompletedOrders(): Promise<Order[]> {
    return this.getOrdersByStatus(OrderStatus.COMPLETED);
  }

  /**
   * Accept a pending order
   */
  async acceptOrder(orderId: string): Promise<OrderResponse> {
    return this.updateOrder(orderId, { status: OrderStatus.ACCEPTED });
  }

  /**
   * Mark order as ready
   */
  async markOrderReady(orderId: string): Promise<OrderResponse> {
    return this.updateOrder(orderId, { status: OrderStatus.READY });
  }

  /**
   * Complete an order
   */
  async completeOrder(orderId: string): Promise<OrderResponse> {
    return this.updateOrder(orderId, { status: OrderStatus.COMPLETED });
  }

  /**
   * Put order on hold
   */
  async holdOrder(orderId: string, reason?: string): Promise<OrderResponse> {
    return this.updateOrder(orderId, { 
      status: OrderStatus.HOLD,
      notes: reason 
    });
  }

  /**
   * Resume order from hold
   */
  async resumeOrder(orderId: string): Promise<OrderResponse> {
    return this.updateOrder(orderId, { status: OrderStatus.PREPARING });
  }

  /**
   * Update order status directly
   */
  async updateOrderStatus(orderId: string, status: OrderStatus): Promise<OrderResponse> {
    return apiClient.patch<OrderResponse>(`${this.basePath}/${orderId}/status?status=${status}`);
  }
}

// Export singleton instance
export const ordersApi = new OrdersApiService();

