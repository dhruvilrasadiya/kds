
import React from "react";
import { Link } from "react-router-dom";
import { Monitor } from "lucide-react";

const FloatingKDS = () => {
  return (
    <Link
      to="/kds"
      className="fixed bottom-6 right-6 bg-pulse-500 hover:bg-pulse-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 z-50"
      title="Kitchen Display System"
    >
      <Monitor className="w-6 h-6" />
    </Link>
  );
};

export default FloatingKDS;
