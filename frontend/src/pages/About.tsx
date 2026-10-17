
import React from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Award, Users, Clock, Heart } from 'lucide-react';

const About = () => {
  const values = [
    {
      icon: <Award className="w-8 h-8" />,
      title: "Excellence",
      description: "We strive for excellence in every dish, using only the finest ingredients and innovative cooking techniques."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Community",
      description: "Building lasting relationships with our customers and contributing positively to our local community."
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: "Innovation",
      description: "Embracing smart technology to enhance your dining experience while maintaining traditional quality."
    },
    {
      icon: <Heart className="w-8 h-8" />,
      title: "Passion",
      description: "Every meal is prepared with love and passion, creating memorable experiences for our guests."
    }
  ];

  const team = [
    {
      name: "Chef Marco Rodriguez",
      role: "Executive Chef",
      image: "https://images.unsplash.com/photo-1583394293214-28ded15ee548?w=300&h=300&fit=crop&crop=face",
      description: "20+ years of culinary excellence"
    },
    {
      name: "Sarah Johnson",
      role: "Restaurant Manager",
      image: "https://images.unsplash.com/photo-1494790108755-2616b612b97c?w=300&h=300&fit=crop&crop=face",
      description: "Expert in smart restaurant operations"
    },
    {
      name: "David Chen",
      role: "Head of Technology",
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop&crop=face",
      description: "Pioneer in restaurant tech innovation"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      
      <div className="pt-20">
        {/* Hero Section */}
        <section className="py-20 bg-gradient-to-r from-pulse-500 to-orange-500 text-white">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-5xl font-bold mb-6">About Pulse Dine-in</h1>
            <p className="text-xl max-w-3xl mx-auto">
              Where cutting-edge technology meets culinary excellence to create unforgettable dining experiences.
            </p>
          </div>
        </section>

        {/* Story Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl font-bold mb-6">Our Story</h2>
                <p className="text-gray-600 text-lg mb-6">
                  Founded in 2020, Pulse Dine-in was born from a vision to revolutionize the restaurant industry through 
                  smart technology and exceptional cuisine. Our founders, a team of experienced restaurateurs and tech 
                  innovators, saw an opportunity to create a dining experience that seamlessly blends tradition with innovation.
                </p>
                <p className="text-gray-600 text-lg mb-6">
                  Today, we're proud to be at the forefront of the smart restaurant movement, using AI-powered kitchen 
                  management, IoT sensors, and data analytics to deliver consistently excellent food while providing 
                  unparalleled efficiency and customer service.
                </p>
                <p className="text-gray-600 text-lg">
                  Every dish tells a story, and every technology solution serves a purpose: to make your dining 
                  experience more enjoyable, efficient, and memorable.
                </p>
              </div>
              <div className="relative">
                <img 
                  src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&h=400&fit=crop" 
                  alt="Restaurant interior"
                  className="rounded-lg shadow-lg"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent rounded-lg"></div>
              </div>
            </div>
          </div>
        </section>

        {/* Values Section */}
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">Our Values</h2>
              <p className="text-gray-600 text-lg">The principles that guide everything we do</p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {values.map((value, index) => (
                <div key={index} className="text-center p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
                  <div className="w-16 h-16 mx-auto mb-4 bg-pulse-100 rounded-full flex items-center justify-center text-pulse-500">
                    {value.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{value.title}</h3>
                  <p className="text-gray-600">{value.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">Meet Our Team</h2>
              <p className="text-gray-600 text-lg">The passionate people behind Pulse Dine-in</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              {team.map((member, index) => (
                <div key={index} className="text-center">
                  <img 
                    src={member.image} 
                    alt={member.name}
                    className="w-48 h-48 mx-auto rounded-full object-cover mb-4 shadow-lg"
                  />
                  <h3 className="text-xl font-semibold mb-2">{member.name}</h3>
                  <p className="text-pulse-500 font-medium mb-2">{member.role}</p>
                  <p className="text-gray-600">{member.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-16 bg-pulse-500 text-white">
          <div className="container mx-auto px-4">
            <div className="grid md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-4xl font-bold mb-2">50K+</div>
                <div className="text-pulse-100">Happy Customers</div>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">100+</div>
                <div className="text-pulse-100">Menu Items</div>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">99%</div>
                <div className="text-pulse-100">Order Accuracy</div>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">4.9★</div>
                <div className="text-pulse-100">Customer Rating</div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <Footer />
    </div>
  );
};

export default About;
