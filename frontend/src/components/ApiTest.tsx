/**
 * API Test Component
 * Simple component to test backend connectivity
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

const ApiTest = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const testConnection = async () => {
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      console.log('Testing API connection to:', apiClient.getConfig().baseURL);
      
      // Test basic health endpoint
      const healthResponse = await apiClient.healthCheck();
      console.log('Health check response:', healthResponse);
      
      // Test root endpoint
      const rootResponse = await apiClient.get('/');
      console.log('Root endpoint response:', rootResponse);
      
      setResult({
        health: healthResponse,
        root: rootResponse,
        timestamp: new Date().toISOString()
      });
    } catch (err: any) {
      console.error('API test failed:', err);
      setError(err.message || 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const testSystemHealth = async () => {
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      console.log('Testing system health endpoint...');
      const response = await apiClient.get('/api/system/health');
      console.log('System health response:', response);
      setResult(response);
    } catch (err: any) {
      console.error('System health test failed:', err);
      setError(err.message || 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const testOrders = async () => {
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      console.log('Testing orders endpoint...');
      const response = await apiClient.get('/api/orders');
      console.log('Orders response:', response);
      setResult(response);
    } catch (err: any) {
      console.error('Orders test failed:', err);
      setError(err.message || 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          API Connection Test
          {result && <CheckCircle className="w-5 h-5 text-green-500" />}
          {error && <XCircle className="w-5 h-5 text-red-500" />}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2 flex-wrap">
          <Button 
            onClick={testConnection} 
            disabled={isLoading}
            variant="outline"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Test Basic Connection
          </Button>
          
          <Button 
            onClick={testSystemHealth} 
            disabled={isLoading}
            variant="outline"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Test System Health
          </Button>
          
          <Button 
            onClick={testOrders} 
            disabled={isLoading}
            variant="outline"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Test Orders API
          </Button>
        </div>

        <div className="text-sm text-gray-600">
          <p><strong>Backend URL:</strong> {apiClient.getConfig().baseURL}</p>
        </div>

        {error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Error:</strong> {error}
            </AlertDescription>
          </Alert>
        )}

        {result && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Success!</strong> API connection is working.
              <details className="mt-2">
                <summary className="cursor-pointer font-medium">View Response</summary>
                <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto max-h-40">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </details>
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ApiTest;
