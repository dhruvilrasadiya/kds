
import React, { useState } from 'react';
import { Plus, Minus } from 'lucide-react';
import { useCart } from '@/contexts/CartContext';

interface MenuItem {
  id: string;
  name: string;
  category: string;
  price: number;
  calories: number;
  image: string;
  description: string;
  addOns: string[];
}

interface MenuItemCardProps {
  item: MenuItem;
}

const MenuItemCard = ({ item }: MenuItemCardProps) => {
  const { cartItems, addToCart, updateQuantity } = useCart();
  const [selectedAddOns, setSelectedAddOns] = useState<string[]>([]);
  
  const cartItem = cartItems.find(cartItem => cartItem.id === item.id);
  const quantity = cartItem?.quantity || 0;

  const handleAddToCart = () => {
    addToCart({
      id: item.id,
      name: item.name,
      price: item.price,
      image: item.image,
      addOns: selectedAddOns,
      category: item.category,
      calories: item.calories
    });
  };

  const handleQuantityChange = (newQuantity: number) => {
    updateQuantity(item.id, newQuantity);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <img
        src={item.image}
        alt={item.name}
        className="w-full h-48 object-cover"
      />
      
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-semibold text-gray-900">{item.name}</h3>
          <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {item.calories} cal
          </span>
        </div>
        
        <p className="text-gray-600 text-sm mb-3">{item.description}</p>
        
        <div className="text-sm text-gray-500 mb-3">
          Category: <span className="capitalize">{item.category}</span>
        </div>

        {item.addOns.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Add-ons:</p>
            <div className="flex flex-wrap gap-1">
              {item.addOns.map(addOn => (
                <button
                  key={addOn}
                  onClick={() => {
                    setSelectedAddOns(prev =>
                      prev.includes(addOn)
                        ? prev.filter(a => a !== addOn)
                        : [...prev, addOn]
                    );
                  }}
                  className={`text-xs px-2 py-1 rounded border ${
                    selectedAddOns.includes(addOn)
                      ? 'bg-pulse-500 text-white border-pulse-500'
                      : 'bg-gray-100 text-gray-700 border-gray-300'
                  }`}
                >
                  {addOn}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <span className="text-xl font-bold text-pulse-600">${item.price}</span>
          
          {quantity === 0 ? (
            <button
              onClick={handleAddToCart}
              className="bg-pulse-500 text-white px-4 py-2 rounded-lg hover:bg-pulse-600 transition-colors flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          ) : (
            <div className="flex items-center space-x-3">
              <button
                onClick={() => handleQuantityChange(quantity - 1)}
                className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300 transition-colors"
              >
                <Minus className="w-4 h-4" />
              </button>
              <span className="font-semibold text-lg animate-pulse">{quantity}</span>
              <button
                onClick={() => handleQuantityChange(quantity + 1)}
                className="w-8 h-8 rounded-full bg-pulse-500 text-white flex items-center justify-center hover:bg-pulse-600 transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MenuItemCard;
