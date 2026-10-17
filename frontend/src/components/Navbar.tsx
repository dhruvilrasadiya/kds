
import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Menu, X, Phone, ShoppingCart } from "lucide-react";
import { Link } from "react-router-dom";
import { useCart } from "@/contexts/CartContext";

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { cartItems } = useCart();

  const cartItemsCount = cartItems.reduce((total, item) => total + item.quantity, 0);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    document.body.style.overflow = !isMenuOpen ? 'hidden' : '';
  };

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 py-2 sm:py-3 md:py-4 transition-all duration-300",
        isScrolled 
          ? "bg-white/95 backdrop-blur-md shadow-sm" 
          : "bg-transparent"
      )}
    >
      <div className="container flex items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center space-x-2">
          {/* <img 
            src="/logo.svg" 
            alt="Pulse Dine-in Logo" 
            className="h-7 sm:h-8" 
          /> */}
          <span className="text-xl font-display font-bold text-pulse-600">Pulse Dine-in</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          <Link to="/" className="nav-link">Home</Link>
          
          <Link to="/menu" className="nav-link">Menu</Link>
          
          <Link to="/about" className="nav-link">About Us</Link>
          <Link to="/contact" className="nav-link">Contact</Link>
          
          <a href="tel:+1234567890" className="flex items-center space-x-2 bg-pulse-500 text-white px-4 py-2 rounded-full hover:bg-pulse-600 transition-colors">
            <Phone className="w-4 h-4" />
            <span>Call Now</span>
          </a>
          
          <Link to="/cart" className="relative flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-full transition-colors">
            <ShoppingCart className="w-4 h-4" />
            <span>Cart</span>
            {cartItemsCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-pulse-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
                {cartItemsCount}
              </span>
            )}
          </Link>
        </nav>

        {/* Mobile menu button */}
        <button 
          className="md:hidden text-gray-700 p-3 focus:outline-none" 
          onClick={toggleMenu}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Navigation */}
      <div className={cn(
        "fixed inset-0 z-40 bg-white flex flex-col pt-16 px-6 md:hidden transition-all duration-300 ease-in-out",
        isMenuOpen ? "opacity-100 translate-x-0" : "opacity-0 translate-x-full pointer-events-none"
      )}>
        <nav className="flex flex-col space-y-6 items-center mt-8">
          <Link to="/" className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" onClick={toggleMenu}>
            Home
          </Link>
          <Link to="/menu" className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" onClick={toggleMenu}>
            Menu
          </Link>
          <Link to="/about" className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" onClick={toggleMenu}>
            About Us
          </Link>
          <Link to="/contact" className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" onClick={toggleMenu}>
            Contact
          </Link>
          <Link to="/cart" className="text-xl font-medium py-3 px-6 w-full text-center rounded-lg hover:bg-gray-100" onClick={toggleMenu}>
            Cart ({cartItemsCount})
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
