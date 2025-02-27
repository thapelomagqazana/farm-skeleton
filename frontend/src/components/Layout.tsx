import React from "react";
import { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-100 text-gray-800">
      {children}
      <footer className="text-center p-4 bg-gray-200 mt-10">
        © {new Date().getFullYear()} FARM Skeleton
      </footer>
    </div>
  );
};

export default Layout;
