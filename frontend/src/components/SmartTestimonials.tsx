
import React from "react";
import { Star } from "lucide-react";

const SmartTestimonials = () => {
  const testimonials = [
    {
      content: "The smart ordering system made our dining experience seamless. We could customize our order, track preparation, and pay contactlessly. The food quality was outstanding!",
      author: "Sarah Johnson",
      role: "Tech Enthusiast",
      rating: 5,
      image: "https://images.unsplash.com/photo-1494790108755-2616b612b97c?w=100&h=100&fit=crop&crop=face"
    },
    {
      content: "As a restaurant manager, I'm impressed by their kitchen display system. Order accuracy improved by 40% and our team can focus more on food quality rather than managing orders.",
      author: "Michael Chen",
      role: "Restaurant Manager",
      rating: 5,
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face"
    },
    {
      content: "The AI-powered recommendations suggested the perfect wine pairing for my meal. The personalized experience made me feel like a VIP customer every time I visit.",
      author: "Emily Rodriguez",
      role: "Food Blogger",
      rating: 5,
      image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face"
    },
    {
      content: "Ordering for our large corporate group was effortless with their smart system. Real-time updates kept everyone informed, and the contactless payment saved us time.",
      author: "David Kim",
      role: "Corporate Executive",
      rating: 5,
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face"
    }
  ];

  return (
    <section className="py-16 bg-white">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">What Our Customers Say</h2>
          <p className="text-xl text-gray-600">
            Discover how our smart restaurant technology enhances the dining experience
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {testimonials.map((testimonial, index) => (
            <div 
              key={index}
              className="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition-shadow duration-300"
            >
              <div className="flex items-center mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                ))}
              </div>
              
              <p className="text-gray-700 mb-6 text-lg leading-relaxed">
                "{testimonial.content}"
              </p>
              
              <div className="flex items-center">
                <img 
                  src={testimonial.image} 
                  alt={testimonial.author}
                  className="w-12 h-12 rounded-full object-cover mr-4"
                />
                <div>
                  <h4 className="font-semibold text-gray-900">{testimonial.author}</h4>
                  <p className="text-gray-600 text-sm">{testimonial.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SmartTestimonials;
