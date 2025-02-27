import React, { useState, useContext, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

/**
 * Navbar component with authentication-based menu options.
 *
 * @returns {JSX.Element} The dynamic navigation bar.
 */
const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  // Ensure AuthContext is not null
  if (!authContext) {
    throw new Error("AuthContext must be used within an AuthProvider");
  }

  const { user, isAuthenticated, logout } = authContext;

  /**
   * Toggles the mobile menu open/close state.
   */
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  /**
   * Handles user logout.
   */
  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  /**
    * Fetch users when authenticated.
    */
    useEffect(() => {
        if (!isAuthenticated) {
        navigate("/signin");
        }
    }, [isAuthenticated, navigate]);
  

  return (
    <nav className="bg-blue-600 text-white shadow-md fixed top-0 left-0 w-full z-50">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        {/* Logo */}
        <Link to="/" className="text-2xl font-bold">
          FARM Starter
        </Link>

        {/* Desktop Menu (Authenticated) */}
        <div className="hidden md:flex space-x-6">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="hover:underline">Dashboard</Link>
              <Link to="/users" className="hover:underline">Users</Link>
              <Link to="/profile" className="hover:underline">My Profile</Link>
              <button onClick={handleLogout} className="hover:underline">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/" className="hover:underline">Home</Link>
              <Link to="/about" className="hover:underline">About</Link>
              <Link to="/signin" className="hover:underline">Sign In</Link>
              <Link to="/register" className="hover:underline">Register</Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden focus:outline-none"
          onClick={toggleMenu}
          aria-label="Toggle navigation menu"
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
      <div
        className={`md:hidden bg-blue-700 overflow-hidden transition-all duration-300 ${
          isOpen ? "max-h-40 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        {isAuthenticated ? (
          <>
            <Link to="/dashboard" className="block py-2 px-4 hover:bg-blue-800" onClick={() => setIsOpen(false)}>
              Dashboard
            </Link>
            <Link to="/users" className="block py-2 px-4 hover:bg-blue-800" onClick={() => setIsOpen(false)}>
              Users
            </Link>
            <Link to="/profile" className="block py-2 px-4 hover:bg-blue-800" onClick={() => setIsOpen(false)}>
              My Profile
            </Link>
            <button onClick={handleLogout} className="block py-2 px-4 hover:bg-blue-800 w-full text-left">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/" className="block py-2 px-4 hover:bg-blue-800" onClick={() => setIsOpen(false)}>
              Home
            </Link>
            <Link to="/about" className="block py-2 px-4 hover:bg-blue-800" onClick={() => setIsOpen(false)}>
              About
            </Link>
            <Link to="/signin" className="block py-2 px-4 hover:bg-blue-800" onClick={() => setIsOpen(false)}>
              Sign In
            </Link>
            <Link to="/register" className="block py-2 px-4 hover:bg-blue-800" onClick={() => setIsOpen(false)}>
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
