
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import WhyOurRestaurant from "@/components/WhyOurRestaurant";
import SmartSystem from "@/components/SmartSystem";
import FeaturedItems from "@/components/FeaturedItems";
import SmartRestaurantFeatures from "@/components/SmartRestaurantFeatures";
import SmartTestimonials from "@/components/SmartTestimonials";
import OfferSlider from "@/components/OfferSlider";
import Footer from "@/components/Footer";
import FloatingKDS from "@/components/FloatingKDS";
import Dashboard from "@/components/Dashboard";
import { Button } from "@/components/ui/button";
import { Monitor, Home, ShoppingCart } from "lucide-react";

const Index = () => {
  const [showDashboard, setShowDashboard] = useState(false);

  // Initialize intersection observer to detect when elements enter viewport
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("animate-fade-in");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );

    const elements = document.querySelectorAll(".animate-on-scroll");
    elements.forEach((el) => observer.observe(el));

    return () => {
      elements.forEach((el) => observer.unobserve(el));
    };
  }, []);

  if (showDashboard) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="pt-16">
          <div className="container mx-auto px-4 py-6">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold">System Dashboard</h1>
              <Button
                variant="outline"
                onClick={() => setShowDashboard(false)}
                className="flex items-center gap-2"
              >
                <Home className="w-4 h-4" />
                Back to Home
              </Button>
            </div>
            <Dashboard />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="space-y-4 sm:space-y-8">
        <Hero />

        {/* Quick Navigation Section */}
        <section className="container mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Quick Access</h2>
            <p className="text-gray-600">Navigate to different sections of our smart kitchen system</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <Link to="/menu" className="group">
              <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 p-6 text-center border-2 border-transparent hover:border-blue-500">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-200 transition-colors">
                  <ShoppingCart className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Browse Menu</h3>
                <p className="text-gray-600">Explore our delicious menu items and place orders</p>
              </div>
            </Link>

            <Link to="/dashboard" className="group">
              <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 p-6 text-center border-2 border-transparent hover:border-green-500">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-green-200 transition-colors">
                  <Monitor className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">System Dashboard</h3>
                <p className="text-gray-600">Monitor kitchen operations and performance metrics</p>
              </div>
            </Link>

            <Link to="/kds" className="group">
              <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 p-6 text-center border-2 border-transparent hover:border-purple-500">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-200 transition-colors">
                  <Home className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Kitchen Display</h3>
                <p className="text-gray-600">Real-time kitchen queue management system</p>
              </div>
            </Link>
          </div>
        </section>

        <WhyOurRestaurant />
        <SmartSystem />
        <FeaturedItems />
        <SmartRestaurantFeatures />
        <SmartTestimonials />
        <OfferSlider />
      </main>
      <Footer />
      <FloatingKDS />

      {/* Dashboard Toggle Button */}
      <Button
        onClick={() => setShowDashboard(true)}
        className="fixed bottom-6 left-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 z-50"
        title="System Dashboard"
      >
        <Monitor className="w-6 h-6" />
      </Button>
    </div>
  );
};

export default Index;
