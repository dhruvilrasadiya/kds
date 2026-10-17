
import React from "react";
import { Smartphone, Wifi, Cpu, Shield, Clock, BarChart } from "lucide-react";

const SmartRestaurantFeatures = () => {
  const features = [
    {
      icon: <Smartphone className="w-6 h-6" />,
      title: "Mobile Ordering",
      description: "Order directly from your smartphone with our intuitive mobile app and QR code menu system.",
      image: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&h=300&fit=crop"
    },
    {
      icon: <Wifi className="w-6 h-6" />,
      title: "IoT Integration",
      description: "Smart sensors monitor temperature, inventory, and customer preferences in real-time.",
      image: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=300&fit=crop"
    },
    {
      icon: <Cpu className="w-6 h-6" />,
      title: "AI Kitchen Management",
      description: "Artificial intelligence optimizes cooking times and ingredient usage for perfect meals.",
      image: "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Contactless Payment",
      description: "Secure, touch-free payment options including mobile wallets and contactless cards.",
      image: "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400&h=300&fit=crop"
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Real-time Tracking",
      description: "Track your order from kitchen to table with live updates and accurate delivery times.",
      image: "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=400&h=300&fit=crop"
    },
    {
      icon: <BarChart className="w-6 h-6" />,
      title: "Smart Analytics",
      description: "Data-driven insights help us personalize your experience and improve service quality.",
      image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop"
    }
  ];

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Smart Restaurant Technology</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Experience the future of dining with our cutting-edge technology that enhances every aspect of your restaurant visit.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300"
            >
              <div className="relative h-48 overflow-hidden">
                <img 
                  src={feature.image} 
                  alt={feature.title}
                  className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-4 left-4 text-white">
                  {feature.icon}
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SmartRestaurantFeatures;
