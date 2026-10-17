/**
 * React hooks for Kitchens API
 * Provides React Query integration for kitchen management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { 
  kitchensApi, 
  CompleteItemRequest,
  KitchenStatusUpdateRequest,
  KitchenStatus,
  getErrorMessage 
} from '@/services/api';

// Query keys
export const kitchenKeys = {
  all: ['kitchens'] as const,
  lists: () => [...kitchenKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...kitchenKeys.lists(), filters] as const,
  details: () => [...kitchenKeys.all, 'detail'] as const,
  detail: (id: string) => [...kitchenKeys.details(), id] as const,
  status: (id: string) => [...kitchenKeys.detail(id), 'status'] as const,
  queue: (id: string) => [...kitchenKeys.detail(id), 'queue'] as const,
  efficiency: (id: string, period?: string) => [...kitchenKeys.detail(id), 'efficiency', period] as const,
  loads: () => [...kitchenKeys.all, 'loads'] as const,
  performance: (id: string, days: number) => [...kitchenKeys.detail(id), 'performance', days] as const,
};

/**
 * Hook to fetch all kitchens
 */
export const useKitchens = () => {
  return useQuery({
    queryKey: kitchenKeys.lists(),
    queryFn: () => kitchensApi.getKitchens(),
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refetch every 2 minutes
  });
};

/**
 * Hook to fetch specific kitchen status
 */
export const useKitchenStatus = (kitchenId: string) => {
  return useQuery({
    queryKey: kitchenKeys.status(kitchenId),
    queryFn: () => kitchensApi.getKitchenStatus(kitchenId),
    enabled: !!kitchenId,
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch kitchen queue
 */
export const useKitchenQueue = (kitchenId: string) => {
  return useQuery({
    queryKey: kitchenKeys.queue(kitchenId),
    queryFn: () => kitchensApi.getKitchenQueue(kitchenId),
    enabled: !!kitchenId,
    staleTime: 15000, // 15 seconds
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};

/**
 * Hook to fetch kitchen efficiency metrics
 */
export const useKitchenEfficiency = (kitchenId: string, period?: string) => {
  return useQuery({
    queryKey: kitchenKeys.efficiency(kitchenId, period),
    queryFn: () => kitchensApi.getKitchenEfficiency(kitchenId, period),
    enabled: !!kitchenId,
    staleTime: 300000, // 5 minutes
  });
};

/**
 * Hook to fetch kitchen loads
 */
export const useKitchenLoads = () => {
  return useQuery({
    queryKey: kitchenKeys.loads(),
    queryFn: () => kitchensApi.getKitchenLoads(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch active kitchens only
 */
export const useActiveKitchens = () => {
  return useQuery({
    queryKey: kitchenKeys.list({ status: KitchenStatus.ACTIVE }),
    queryFn: () => kitchensApi.getActiveKitchens(),
    staleTime: 60000,
    refetchInterval: 120000,
  });
};

/**
 * Hook to fetch kitchen performance
 */
export const useKitchenPerformance = (kitchenId: string, days: number = 7) => {
  return useQuery({
    queryKey: kitchenKeys.performance(kitchenId, days),
    queryFn: () => kitchensApi.getKitchenPerformance(kitchenId, days),
    enabled: !!kitchenId,
    staleTime: 600000, // 10 minutes
  });
};

/**
 * Hook to update kitchen status
 */
export const useUpdateKitchenStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (statusUpdate: KitchenStatusUpdateRequest) =>
      kitchensApi.updateKitchenStatus(statusUpdate),
    onSuccess: (data, variables) => {
      // Invalidate kitchen-related queries
      queryClient.invalidateQueries({ queryKey: kitchenKeys.detail(variables.kitchen_id) });
      queryClient.invalidateQueries({ queryKey: kitchenKeys.lists() });
      toast.success(`Kitchen ${variables.kitchen_id} status updated to ${variables.status}`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to update kitchen status: ${message}`);
    },
  });
};

/**
 * Hook to complete a queue item
 */
export const useCompleteItem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (completeRequest: CompleteItemRequest) =>
      kitchensApi.completeItem(completeRequest),
    onSuccess: (data, variables) => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: kitchenKeys.all });
      queryClient.invalidateQueries({ queryKey: ['orders'] }); // Also invalidate orders
      toast.success(`Item completed successfully!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to complete item: ${message}`);
    },
  });
};

/**
 * Hook to activate a kitchen
 */
export const useActivateKitchen = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (kitchenId: string) => kitchensApi.activateKitchen(kitchenId),
    onSuccess: (data, kitchenId) => {
      queryClient.invalidateQueries({ queryKey: kitchenKeys.detail(kitchenId) });
      queryClient.invalidateQueries({ queryKey: kitchenKeys.lists() });
      toast.success(`Kitchen ${kitchenId} activated!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to activate kitchen: ${message}`);
    },
  });
};

/**
 * Hook to set kitchen to maintenance
 */
export const useSetKitchenMaintenance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ kitchenId, notes }: { kitchenId: string; notes?: string }) =>
      kitchensApi.setKitchenMaintenance(kitchenId, notes),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: kitchenKeys.detail(variables.kitchenId) });
      queryClient.invalidateQueries({ queryKey: kitchenKeys.lists() });
      toast.warning(`Kitchen ${variables.kitchenId} set to maintenance mode`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to set kitchen to maintenance: ${message}`);
    },
  });
};

/**
 * Hook to set kitchen offline
 */
export const useSetKitchenOffline = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ kitchenId, notes }: { kitchenId: string; notes?: string }) =>
      kitchensApi.setKitchenOffline(kitchenId, notes),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: kitchenKeys.detail(variables.kitchenId) });
      queryClient.invalidateQueries({ queryKey: kitchenKeys.lists() });
      toast.error(`Kitchen ${variables.kitchenId} set offline`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to set kitchen offline: ${message}`);
    },
  });
};

/**
 * Hook to emergency stop kitchen
 */
export const useEmergencyStop = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ kitchenId, reason }: { kitchenId: string; reason: string }) =>
      kitchensApi.emergencyStop(kitchenId, reason),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: kitchenKeys.all });
      toast.error(`Emergency stop activated for kitchen ${variables.kitchenId}`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to emergency stop kitchen: ${message}`);
    },
  });
};

/**
 * Hook to resume kitchen operations
 */
export const useResumeOperations = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (kitchenId: string) => kitchensApi.resumeOperations(kitchenId),
    onSuccess: (data, kitchenId) => {
      queryClient.invalidateQueries({ queryKey: kitchenKeys.all });
      toast.success(`Kitchen ${kitchenId} operations resumed!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to resume kitchen operations: ${message}`);
    },
  });
};

/**
 * Hook to create a new kitchen
 */
export const useCreateKitchen = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (kitchenData: {
      name: string;
      capacity: number;
      location?: string;
      specialties?: string[];
      status?: string;
    }) => kitchensApi.createKitchen(kitchenData),
    onSuccess: () => {
      // Invalidate kitchens list to refresh data
      queryClient.invalidateQueries({ queryKey: kitchenKeys.lists() });
      toast.success('Kitchen created successfully');
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to create kitchen: ${message}`);
    },
  });
};

