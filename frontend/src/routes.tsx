import React from "react";
import { RouteObject } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";
import Signin from "./pages/Signin";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./routes/ProtectedRoute"; 

/**
 * Defines all application routes.
 */
const routes: RouteObject[] = [
  { path: "/", element: <Home /> },
  { path: "/about", element: <About /> },
  { path: "/register", element: <Register /> },
  { path: "/signin", element: <Signin /> },
  {
    path: "/dashboard",
    element: <ProtectedRoute />, // Protects Dashboard Route
    children: [{ path: "", element: <Dashboard /> }],
  },
  { path: "*", element: <NotFound /> },
];

export default routes;
