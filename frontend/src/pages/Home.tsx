import React from "react";
import Hero from "../components/Hero";
import APIList from "../components/APIList";
import FeatureCard from "../components/FeatureCard";

/**
 * Home page showcasing the FARM Skeleton Starter Pack.
 *
 * @returns {JSX.Element} The Home component.
 */
const Home: React.FC = () => {
  return (  
    <>
      <Hero />
      <div className="container mx-auto p-6">
        {/* Features Section */}
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard title="⚡ FastAPI Backend" description="Build high-performance APIs with Python and FastAPI." />
          <FeatureCard title="🚀 React + Vite Frontend" description="Leverage modern React with Vite for fast development." />
          <FeatureCard title="🗄️ MongoDB Database" description="Efficiently store and retrieve data with MongoDB." />
          <FeatureCard title="🔒 Authentication" description="Secure user authentication with JWT." />
          <FeatureCard title="🛠️ CRUD Operations" description="Easily manage users with Create, Read, Update, and Delete endpoints." />
          <FeatureCard title="🎨 Tailwind CSS" description="Create beautiful and responsive UI with Tailwind CSS." />
        </div>

        {/* API Endpoints Section */}
        <div className="mt-10">
          <APIList />
        </div>

        {/* Call to Action: Get Started with the Template */}
        <div className="mt-12 bg-gray-100 p-6 rounded-lg text-center">
          <h2 className="text-xl font-semibold text-gray-900">
            Want to build your own project with FARM Stack?
          </h2>
          <p className="text-gray-700 mt-2">
            Get started quickly by using our <strong>FARM Skeleton Starter Pack</strong>.  
            Clone the template from GitHub, customize the frontend and backend, and build your application effortlessly.
          </p>
          <a
            href="https://github.com/thapelomagqazana/farm-skeleton"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded transition"
          >
            🚀 Clone the Template
          </a>
        </div>
      </div>
    </>
  );
};

export default Home;
