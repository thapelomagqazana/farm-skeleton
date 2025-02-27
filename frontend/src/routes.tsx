import React from "react";
import { RouteObject } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";

const routes: RouteObject[] = [
  { path: "/", element: <Home /> },
  { path: "/about", element: <About /> },
  { path: "/register", element: <Register /> },
  { path: "*", element: <NotFound /> },
];

export default routes;
