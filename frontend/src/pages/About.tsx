import React from "react";
import FeatureCard from "../components/FeatureCard";
import Heading from "../components/Heading";

/**
 * About Page introducing the FARM Skeleton Starter Pack.
 *
 * @returns {JSX.Element} The About page.
 */
const About: React.FC = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100 p-6">
      <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-3xl">
        <Heading text="About FARM Skeleton Starter Pack" />
        <p className="text-gray-600 mb-4">
          The FARM Skeleton Starter Pack provides a clean architecture for FastAPI, React, MongoDB, and Tailwind CSS.
          It includes essential CRUD operations, authentication, and structured routes.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FeatureCard title="🔑 Authentication" description="Secure user authentication with JWT." />
          <FeatureCard title="🛠 User Management" description="CRUD operations for managing users." />
          <FeatureCard title="🚀 FastAPI Backend" description="Optimized backend using FastAPI and MongoDB." />
          <FeatureCard title="🎨 Tailwind CSS" description="Modern UI styling with Tailwind." />
        </div>
      </div>
    </div>
  );
};

export default About;
