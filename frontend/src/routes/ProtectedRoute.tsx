import React, { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

/**
 * Protects routes by ensuring only authenticated users can access them.
 */
const ProtectedRoute: React.FC = () => {
  const auth = useContext(AuthContext);

  // Redirect to sign-in if not authenticated
  return auth?.isAuthenticated ? <Outlet /> : <Navigate to="/signin" />;
};

export default ProtectedRoute;
