import React, { useState } from "react";
import { Link } from "react-router-dom";

/**
 * Navbar component with responsive design.
 *
 * @returns {JSX.Element} The navigation bar.
 */
const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        {/* Logo */}
        <Link to="/" className="text-2xl font-bold">
          FARM Starter
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex space-x-6">
          <Link to="/" className="hover:underline">Home</Link>
          <Link to="/about" className="hover:underline">About</Link>
          <Link to="/auth/signin" className="hover:underline">Sign In</Link>
          <Link to="/auth/signup" className="hover:underline">Register</Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden focus:outline-none"
          onClick={() => setIsOpen(!isOpen)}
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            {isOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {isOpen && (
        <div className="md:hidden bg-blue-700 py-2 space-y-2 text-center">
          <Link to="/" className="block py-2 hover:bg-blue-800">Home</Link>
          <Link to="/about" className="block py-2 hover:bg-blue-800">About</Link>
          <Link to="/auth/signin" className="block py-2 hover:bg-blue-800">Sign In</Link>
          <Link to="/auth/signup" className="block py-2 hover:bg-blue-800">Register</Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
