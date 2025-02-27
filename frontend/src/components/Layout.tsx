import React from "react";
import { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-100 text-gray-800 mt-10">
      {children}
      <footer className="text-center p-4 bg-gray-200 mt-10 text-gray-700">
        <p>© {new Date().getFullYear()} FARM Skeleton. All rights reserved.</p>
        <p className="text-sm mt-1">
            Built with ❤️ by{" "}
            <a
            href="https://github.com/thapelomagqazana"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
            >
            Thapelo Magqazana
            </a>{" "}
            and the Open Source Community.
        </p>
    </footer>
    </div>
  );
};

export default Layout;
