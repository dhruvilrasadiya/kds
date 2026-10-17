import React from "react";
import { Link } from "react-router-dom";
import { Clock, Utensils, Coffee, Cookie } from "lucide-react";

const MegaMenu = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  const menuCategories = [
    {
      title: "Appetizers",
      icon: <Utensils className="w-5 h-5" />,
      image: "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=300&h=200&fit=crop",
      items: [
        { name: "Spring Rolls", href: "/menu?category=appetizers" },
        { name: "Chicken Wings", href: "/menu?category=appetizers" },
        { name: "Nachos", href: "/menu?category=appetizers" },
        { name: "Bruschetta", href: "/menu?category=appetizers" },
        { name: "Mozzarella Sticks", href: "/menu?category=appetizers" },
        { name: "Garlic Bread", href: "/menu?category=appetizers" },
      ]
    },
    {
      title: "Main Course",
      icon: <Utensils className="w-5 h-5" />,
      image: "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300&h=200&fit=crop",
      items: [
        { name: "Grilled Chicken", href: "/menu?category=main" },
        { name: "Beef Steak", href: "/menu?category=main" },
        { name: "Pasta Carbonara", href: "/menu?category=main" },
        { name: "Margherita Pizza", href: "/menu?category=main" },
        { name: "Fish & Chips", href: "/menu?category=main" },
        { name: "Lamb Curry", href: "/menu?category=main" },
      ]
    },
    {
      title: "Desserts",
      icon: <Cookie className="w-5 h-5" />,
      image: "https://images.unsplash.com/photo-1551024506-0bccd828d307?w=300&h=200&fit=crop",
      items: [
        { name: "Chocolate Cake", href: "/menu?category=desserts" },
        { name: "Ice Cream", href: "/menu?category=desserts" },
        { name: "Tiramisu", href: "/menu?category=desserts" },
        { name: "Cheesecake", href: "/menu?category=desserts" },
        { name: "Apple Pie", href: "/menu?category=desserts" },
        { name: "Crème Brûlée", href: "/menu?category=desserts" },
      ]
    },
    {
      title: "Beverages",
      icon: <Coffee className="w-5 h-5" />,
      image: "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=300&h=200&fit=crop",
      items: [
        { name: "Espresso", href: "/menu?category=beverages" },
        { name: "Fresh Orange Juice", href: "/menu?category=beverages" },
        { name: "Green Smoothie", href: "/menu?category=beverages" },
        { name: "Mojito", href: "/menu?category=beverages" },
        { name: "Hot Chocolate", href: "/menu?category=beverages" },
        { name: "Iced Tea", href: "/menu?category=beverages" },
      ]
    }
  ];

  if (!isOpen) return null;

  return (
    <div 
      className="absolute left-0 top-full w-[90vw] max-w-6xl bg-white shadow-lg border-t border-gray-200 z-50"
      style={{ minWidth: 300 }}
      onMouseEnter={(e) => e.stopPropagation()}
      onMouseLeave={onClose}
    >
      <div className="px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {menuCategories.map((category) => (
            <div key={category.title} className="space-y-4">
              <div className="relative">
                <img 
                  src={category.image} 
                  alt={category.title}
                  className="w-full h-32 object-cover rounded-lg"
                />
                <div className="absolute inset-0 bg-black bg-opacity-30 rounded-lg flex items-center justify-center">
                  <div className="text-white text-center">
                    {category.icon}
                    <h3 className="text-lg font-semibold mt-2">{category.title}</h3>
                  </div>
                </div>
              </div>
              <ul className="space-y-2">
                {category.items.map((item) => (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className="text-gray-600 hover:text-pulse-500 transition-colors block py-1"
                      onClick={onClose}
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const Navbar = () => {
  const [isOpen, setIsOpen] = React.useState(false);

  const handleToggle = () => {
    setIsOpen((prev) => !prev);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  
};

export default Navbar;
