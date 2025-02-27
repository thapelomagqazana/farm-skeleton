import React from "react";
import { BrowserRouter as Router, useRoutes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Layout from "./components/Layout";
import routes from "./routes";

const AppRoutes = () => {
  return useRoutes(routes);
};

const App: React.FC = () => {
  return (
    <Router>
      <Navbar />
      <Layout>
        <AppRoutes />
      </Layout>
    </Router>
  );
};

export default App;
