
import React from "react";
import { Truck, ChefHat, Heart } from "lucide-react";

const WhyOurRestaurant = () => {
  const features = [
    {
      icon: Truck,
      title: "Fast Delivery",
      description: "Quick and reliable delivery to your doorstep within 30 minutes"
    },
    {
      icon: ChefHat,
      title: "Expert Chefs",
      description: "Professionally trained chefs with years of culinary expertise"
    },
    {
      icon: Heart,
      title: "Made with Love",
      description: "Every dish is prepared with care and passion for authentic flavors"
    }
  ];

  return (
    <section className="section-container bg-gray-50">
      <div className="text-center mb-12">
        <h2 className="section-title mb-4">Why Our Restaurant?</h2>
        <p className="section-subtitle">Discover what makes us special</p>
      </div>
      
      <div className="grid md:grid-cols-3 gap-8">
        {features.map((feature, index) => (
          <div 
            key={index}
            className="feature-card bg-white text-center animate-on-scroll"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="w-16 h-16 mx-auto mb-6 bg-pulse-100 rounded-full flex items-center justify-center">
              <feature.icon className="w-8 h-8 text-pulse-500" />
            </div>
            <h3 className="text-xl font-semibold mb-4">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default WhyOurRestaurant;
