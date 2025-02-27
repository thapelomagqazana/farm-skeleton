import React from "react";
import { Link } from "react-router-dom";

/**
 * Not Found (404) Page for unknown routes.
 *
 * @returns {JSX.Element} The 404 error page.
 */
const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col justify-center items-center min-h-screen bg-gray-100 text-center">
      <h1 className="text-6xl font-bold text-red-600">404</h1>
      <p className="text-lg text-gray-600">Oops! The page you're looking for doesn't exist.</p>
      <Link to="/" className="mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition">
        Go Home
      </Link>
    </div>
  );
};

export default NotFound;
