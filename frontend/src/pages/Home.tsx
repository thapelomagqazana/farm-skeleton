import React from "react";
import Hero from "../components/Hero";
import APIList from "../components/APIList";
import Layout from "../components/Layout";
import FeatureCard from "../components/FeatureCard";

const Home: React.FC = () => {
  return (
    <Layout>
      <Hero />
      <div className="container mx-auto p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard title="FastAPI Backend" description="Build powerful APIs with Python and FastAPI." />
          <FeatureCard title="React + Vite Frontend" description="Modern React setup using Vite for blazing-fast development." />
          <FeatureCard title="MongoDB Database" description="Seamlessly store and retrieve user data using MongoDB." />
          <FeatureCard title="Authentication" description="Secure sign-in and JWT authentication." />
          <FeatureCard title="CRUD Operations" description="Manage users with Create, Read, Update, Delete API endpoints." />
          <FeatureCard title="Tailwind CSS" description="Beautiful and responsive UI with Tailwind CSS." />
        </div>
        <div className="mt-10">
          <APIList />
        </div>
      </div>
    </Layout>
  );
};

export default Home;
