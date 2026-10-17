/**
 * Dashboard Page
 * Dedicated page for system dashboard with navigation
 */

import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Dashboard from '@/components/Dashboard';
import { Button } from '@/components/ui/button';
import { Home, Settings, BarChart3 } from 'lucide-react';

const DashboardPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="pt-16">
        <div className="container mx-auto px-4 py-6">
          {/* Header with Navigation */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
            <div>
              <h1 className="text-3xl font-bold">System Dashboard</h1>
              <p className="text-gray-600 mt-1">Real-time kitchen management overview</p>
            </div>
            
            <div className="flex items-center gap-2">
              <Link to="/">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <Home className="w-4 h-4" />
                  Home
                </Button>
              </Link>
              
              <Link to="/analytics">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Analytics
                </Button>
              </Link>
              
              <Link to="/settings">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Settings
                </Button>
              </Link>
            </div>
          </div>

          {/* Dashboard Component */}
          <Dashboard />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
