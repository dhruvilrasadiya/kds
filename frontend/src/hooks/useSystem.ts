/**
 * React hooks for System API
 * Provides React Query integration for system management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { 
  systemApi, 
  getErrorMessage 
} from '@/services/api';

// Query keys
export const systemKeys = {
  all: ['system'] as const,
  health: () => [...systemKeys.all, 'health'] as const,
  metrics: () => [...systemKeys.all, 'metrics'] as const,
  learningReport: () => [...systemKeys.all, 'learning-report'] as const,
  config: () => [...systemKeys.all, 'config'] as const,
  logs: (params?: any) => [...systemKeys.all, 'logs', params] as const,
  statistics: () => [...systemKeys.all, 'statistics'] as const,
  backups: () => [...systemKeys.all, 'backups'] as const,
  connectivity: () => [...systemKeys.all, 'connectivity'] as const,
  version: () => [...systemKeys.all, 'version'] as const,
};

/**
 * Hook to fetch system health
 */
export const useSystemHealth = () => {
  return useQuery({
    queryKey: systemKeys.health(),
    queryFn: () => systemApi.getHealth(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch system metrics
 */
export const useSystemMetrics = () => {
  return useQuery({
    queryKey: systemKeys.metrics(),
    queryFn: () => systemApi.getMetrics(),
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refetch every 2 minutes
  });
};

/**
 * Hook to fetch learning report
 */
export const useLearningReport = () => {
  return useQuery({
    queryKey: systemKeys.learningReport(),
    queryFn: () => systemApi.getLearningReport(),
    staleTime: 600000, // 10 minutes
    refetchInterval: 1800000, // Refetch every 30 minutes
  });
};

/**
 * Hook to fetch system configuration
 */
export const useSystemConfig = () => {
  return useQuery({
    queryKey: systemKeys.config(),
    queryFn: () => systemApi.getConfig(),
    staleTime: 300000, // 5 minutes
  });
};

/**
 * Hook to fetch system logs
 */
export const useSystemLogs = (params?: {
  level?: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  limit?: number;
  since?: string;
}) => {
  return useQuery({
    queryKey: systemKeys.logs(params),
    queryFn: () => systemApi.getLogs(params),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

/**
 * Hook to fetch system statistics
 */
export const useSystemStatistics = () => {
  return useQuery({
    queryKey: systemKeys.statistics(),
    queryFn: () => systemApi.getStatistics(),
    staleTime: 300000, // 5 minutes
    refetchInterval: 600000, // Refetch every 10 minutes
  });
};

/**
 * Hook to fetch available backups
 */
export const useBackups = () => {
  return useQuery({
    queryKey: systemKeys.backups(),
    queryFn: () => systemApi.getBackups(),
    staleTime: 300000, // 5 minutes
  });
};

/**
 * Hook to test system connectivity
 */
export const useSystemConnectivity = () => {
  return useQuery({
    queryKey: systemKeys.connectivity(),
    queryFn: () => systemApi.testConnectivity(),
    staleTime: 60000, // 1 minute
    refetchInterval: 300000, // Refetch every 5 minutes
  });
};

/**
 * Hook to fetch system version
 */
export const useSystemVersion = () => {
  return useQuery({
    queryKey: systemKeys.version(),
    queryFn: () => systemApi.getVersion(),
    staleTime: Infinity, // Version doesn't change often
  });
};

/**
 * Hook to reload system configuration
 */
export const useReloadConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => systemApi.reloadConfig(),
    onSuccess: () => {
      // Invalidate config and related queries
      queryClient.invalidateQueries({ queryKey: systemKeys.config() });
      queryClient.invalidateQueries({ queryKey: systemKeys.health() });
      toast.success('System configuration reloaded successfully!');
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to reload configuration: ${message}`);
    },
  });
};

/**
 * Hook to update system configuration
 */
export const useUpdateConfig = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Partial<{
      max_starvation_count: number;
      synchronization_window_minutes: number;
      performance_history_days: number;
      debug_mode: boolean;
    }>) => systemApi.updateConfig(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: systemKeys.config() });
      toast.success('System configuration updated successfully!');
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to update configuration: ${message}`);
    },
  });
};

/**
 * Hook to clear system logs
 */
export const useClearLogs = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => systemApi.clearLogs(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: systemKeys.logs() });
      toast.success('System logs cleared successfully!');
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to clear logs: ${message}`);
    },
  });
};

/**
 * Hook to export system data
 */
export const useExportData = () => {
  return useMutation({
    mutationFn: (format: 'json' | 'csv' | 'excel' = 'json') => systemApi.exportData(format),
    onSuccess: (blob, format) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `system-data-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success(`System data exported as ${format.toUpperCase()}!`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to export data: ${message}`);
    },
  });
};

/**
 * Hook to import system data
 */
export const useImportData = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => systemApi.importData(file),
    onSuccess: () => {
      // Invalidate all queries as data might have changed
      queryClient.invalidateQueries();
      toast.success('System data imported successfully!');
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to import data: ${message}`);
    },
  });
};

/**
 * Hook to create system backup
 */
export const useCreateBackup = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => systemApi.createBackup(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: systemKeys.backups() });
      toast.success(`Backup created successfully! ID: ${data.backup_id}`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to create backup: ${message}`);
    },
  });
};

/**
 * Hook to restore from backup
 */
export const useRestoreBackup = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (backupId: string) => systemApi.restoreBackup(backupId),
    onSuccess: () => {
      // Invalidate all queries as system state has changed
      queryClient.invalidateQueries();
      toast.success('System restored from backup successfully!');
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to restore from backup: ${message}`);
    },
  });
};

/**
 * Hook to delete backup
 */
export const useDeleteBackup = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (backupId: string) => systemApi.deleteBackup(backupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: systemKeys.backups() });
      toast.success('Backup deleted successfully!');
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      toast.error(`Failed to delete backup: ${message}`);
    },
  });
};
