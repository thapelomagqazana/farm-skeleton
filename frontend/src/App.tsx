import React from "react";
import { BrowserRouter as Router, useRoutes } from "react-router-dom";
import routes from "./routes";

const AppRoutes = () => {
  return useRoutes(routes);
};

const App: React.FC = () => {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
};

export default App;
