/**
 * Dashboard Component
 * Real-time system overview with backend integration
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Activity,
  Clock,
  Users,
  ChefHat,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';
import { useDashboardData, useSystemHealth } from '@/hooks';
import ApiTest from './ApiTest';

const Dashboard = () => {
  const { 
    summary, 
    queue, 
    load, 
    alerts, 
    health,
    isLoading,
    isError,
    refetch 
  } = useDashboardData();

  const systemHealth = useSystemHealth();

  if (isError) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Failed to load dashboard data. Please check your connection to the backend.
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => refetch()} 
              className="ml-2"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Kitchen Management Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time system overview and monitoring</p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          {systemHealth.data && (
            <Badge 
              variant={systemHealth.data.status === 'healthy' ? 'default' : 'destructive'}
              className="flex items-center gap-1"
            >
              {systemHealth.data.status === 'healthy' ? (
                <CheckCircle className="h-3 w-3" />
              ) : (
                <XCircle className="h-3 w-3" />
              )}
              {systemHealth.data.status}
            </Badge>
          )}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Orders Today</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summary.data?.total_orders_today || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {summary.data?.completed_orders_today || 0} completed
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Completion Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summary.data?.average_completion_time || 0}m
                </div>
                <p className="text-xs text-muted-foreground">
                  Target: 15-20 minutes
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Kitchens</CardTitle>
            <ChefHat className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-12" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summary.data?.active_kitchens || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {queue.data?.total_items || 0} items in queue
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Efficiency Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {summary.data?.efficiency_score || 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  {summary.data?.alerts_count || 0} active alerts
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Alerts Section */}
      {alerts.data?.alerts && alerts.data.alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              Starvation Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alerts.data.alerts.slice(0, 5).map((alert, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                  <div>
                    <p className="font-medium">Order {alert.order_id}</p>
                    <p className="text-sm text-gray-600">
                      Item {alert.item_id} • Wait time: {alert.wait_time_minutes}m
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* API Connection Test */}
      <div className="mb-6">
        <ApiTest />
      </div>

      {/* System Load */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Current System Load</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Total Orders</span>
                  <span className="text-sm">{load.data?.total_orders || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Average Wait Time</span>
                  <span className="text-sm">{load.data?.average_wait_time || 0}m</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">System Efficiency</span>
                  <span className="text-sm">{load.data?.system_efficiency || 0}%</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Health Indicators</CardTitle>
          </CardHeader>
          <CardContent>
            {health.isLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            ) : health.data?.indicators ? (
              <div className="space-y-3">
                {health.data.indicators.slice(0, 4).map((indicator, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{indicator.name}</span>
                    <Badge 
                      variant={
                        indicator.status === 'good' ? 'default' : 
                        indicator.status === 'warning' ? 'secondary' : 'destructive'
                      }
                    >
                      {indicator.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No health data available</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
