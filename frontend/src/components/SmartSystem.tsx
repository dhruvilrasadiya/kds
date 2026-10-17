
import React from "react";
import { MapPin, Utensils, Clock } from "lucide-react";

const SmartSystem = () => {
  return (
    <section className="section-container">
      <div className="text-center mb-12">
        <h2 className="section-title mb-4">Smart Restaurant Management</h2>
        <p className="section-subtitle">Intelligent routing in menu, delivery, and kitchen management system</p>
      </div>
      
      <div className="grid md:grid-cols-3 gap-8">
        <div className="text-center p-6 rounded-xl bg-gradient-to-br from-pulse-50 to-orange-50 hover:shadow-lg transition-shadow">
          <div className="w-16 h-16 mx-auto mb-6 bg-pulse-500 rounded-full flex items-center justify-center">
            <MapPin className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-semibold mb-4">Smart Routing</h3>
          <p className="text-gray-600">Optimized delivery routes for faster service</p>
        </div>
        
        <div className="text-center p-6 rounded-xl bg-gradient-to-br from-pulse-50 to-orange-50 hover:shadow-lg transition-shadow">
          <div className="w-16 h-16 mx-auto mb-6 bg-pulse-500 rounded-full flex items-center justify-center">
            <Utensils className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-semibold mb-4">Kitchen Management</h3>
          <p className="text-gray-600">Real-time kitchen display system for efficient cooking</p>
        </div>
        
        <div className="text-center p-6 rounded-xl bg-gradient-to-br from-pulse-50 to-orange-50 hover:shadow-lg transition-shadow">
          <div className="w-16 h-16 mx-auto mb-6 bg-pulse-500 rounded-full flex items-center justify-center">
            <Clock className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-semibold mb-4">Order Tracking</h3>
          <p className="text-gray-600">Live order tracking from kitchen to delivery</p>
        </div>
      </div>
    </section>
  );
};

export default SmartSystem;
