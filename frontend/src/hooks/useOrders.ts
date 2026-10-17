/**
 * React hooks for Orders API
 * Provides React Query integration for order management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { 
  ordersApi, 
  CreateOrderRequest, 
  UpdateOrderRequest, 
  Order, 
  OrderStatus,
  getErrorMessage 
} from '@/services/api';

// Query keys
export const orderKeys = {
  all: ['orders'] as const,
  lists: () => [...orderKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...orderKeys.lists(), filters] as const,
  details: () => [...orderKeys.all, 'detail'] as const,
  detail: (id: string) => [...orderKeys.details(), id] as const,
  history: (id: string) => [...orderKeys.detail(id), 'history'] as const,
};

/**
 * Hook to fetch all orders with optional filtering
 */
export const useOrders = (params?: {
  status?: OrderStatus;
  customer_id?: string;
  limit?: number;
  offset?: number;
}) => {
  return useQuery({
    queryKey: orderKeys.list(params || {}),
    queryFn: () => ordersApi.getOrders(params),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch a specific order
 */
export const useOrder = (orderId: string) => {
  return useQuery({
    queryKey: orderKeys.detail(orderId),
    queryFn: () => ordersApi.getOrder(orderId),
    enabled: !!orderId,
    staleTime: 30000,
  });
};

/**
 * Hook to fetch orders by status
 */
export const useOrdersByStatus = (status: OrderStatus) => {
  return useQuery({
    queryKey: orderKeys.list({ status }),
    queryFn: () => ordersApi.getOrdersByStatus(status),
    staleTime: 15000, // 15 seconds for active orders
    refetchInterval: status === OrderStatus.COMPLETED ? 300000 : 30000, // Less frequent for completed
  });
};

/**
 * Hook to fetch pending orders
 */
export const usePendingOrders = () => {
  return useQuery({
    queryKey: orderKeys.list({ status: OrderStatus.PENDING }),
    queryFn: () => ordersApi.getPendingOrders(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 15000, // Refetch every 15 seconds
  });
};

/**
 * Hook to fetch active orders
 */
export const useActiveOrders = () => {
  return useQuery({
    queryKey: orderKeys.list({ active: true }),
    queryFn: () => ordersApi.getActiveOrders(),
    staleTime: 10000,
    refetchInterval: 15000,
  });
};

/**
 * Hook to create a new order
 */
export const useCreateOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderData: CreateOrderRequest) => ordersApi.createOrder(orderData),
    onSuccess: (data) => {
      // Invalidate and refetch orders
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      toast.success(`Order ${data.order?.order_id} created successfully!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to create order: ${message}`);
    },
  });
};

/**
 * Hook to update an order
 */
export const useUpdateOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, updateData }: { orderId: string; updateData: UpdateOrderRequest }) =>
      ordersApi.updateOrder(orderId, updateData),
    onSuccess: (data, variables) => {
      // Update specific order in cache
      queryClient.setQueryData(orderKeys.detail(variables.orderId), data);
      // Invalidate orders list
      queryClient.invalidateQueries({ queryKey: orderKeys.lists() });
      toast.success(`Order ${variables.orderId} updated successfully!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to update order: ${message}`);
    },
  });
};

/**
 * Hook to cancel an order
 */
export const useCancelOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) =>
      ordersApi.cancelOrder(orderId, reason),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      toast.success(`Order ${variables.orderId} cancelled successfully!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to cancel order: ${message}`);
    },
  });
};

/**
 * Hook to accept an order
 */
export const useAcceptOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) => ordersApi.acceptOrder(orderId),
    onSuccess: (data, orderId) => {
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      toast.success(`Order ${orderId} accepted!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to accept order: ${message}`);
    },
  });
};

/**
 * Hook to mark order as ready
 */
export const useMarkOrderReady = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) => ordersApi.markOrderReady(orderId),
    onSuccess: (data, orderId) => {
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      toast.success(`Order ${orderId} is ready for delivery!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to mark order as ready: ${message}`);
    },
  });
};

/**
 * Hook to complete an order
 */
export const useCompleteOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) => ordersApi.completeOrder(orderId),
    onSuccess: (data, orderId) => {
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      toast.success(`Order ${orderId} completed!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to complete order: ${message}`);
    },
  });
};

/**
 * Hook to put order on hold
 */
export const useHoldOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) =>
      ordersApi.holdOrder(orderId, reason),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      toast.warning(`Order ${variables.orderId} put on hold`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to hold order: ${message}`);
    },
  });
};

/**
 * Hook to resume order from hold
 */
export const useResumeOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) => ordersApi.resumeOrder(orderId),
    onSuccess: (data, orderId) => {
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
      toast.success(`Order ${orderId} resumed!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to resume order: ${message}`);
    },
  });
};

/**
 * Hook to update order status directly
 */
export const useUpdateOrderStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, status }: { orderId: string; status: OrderStatus }) =>
      ordersApi.updateOrderStatus(orderId, status),
    onSuccess: (data, variables) => {
      // Update specific order in cache
      queryClient.setQueryData(orderKeys.detail(variables.orderId), data);
      // Invalidate orders list
      queryClient.invalidateQueries({ queryKey: orderKeys.lists() });
      toast.success(`Order ${variables.orderId} status updated to ${variables.status}`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to update order status: ${message}`);
    },
  });
};

