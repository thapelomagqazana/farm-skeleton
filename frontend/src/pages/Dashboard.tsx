import React, { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { fetchUsers } from "../api/userService";
import DashboardCard from "../components/DashboardCard";
import UserTable from "../components/UserTable";
import ActionButton from "../components/ActionButton";
import { useNavigate } from "react-router-dom";

/**
 * Dashboard page for authenticated users.
 *
 * @returns {JSX.Element} The dashboard UI.
 */
const Dashboard: React.FC = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  if (!authContext) {
    throw new Error("AuthContext must be used within an AuthProvider");
  }

  const { user, isAuthenticated, logout } = authContext;
  const [users, setUsers] = useState<any[]>([]);

  /**
   * Fetch users when authenticated.
   */
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/signin");
    }

    const loadUsers = async () => {
      try {
        const data = await fetchUsers();
        setUsers(data);
      } catch (error) {
        console.error("Failed to load users", error);
      }
    };

    loadUsers();
  }, [isAuthenticated, navigate]);

  return (
    <div className="container mx-auto p-6 mt-20">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard title="Total Users" value={users.length} />
        <DashboardCard title="Role" value={user?.role || "User"} />
        <DashboardCard title="Email" value={user?.email} />
      </div>

      <div className="mt-10">
        <h3 className="text-2xl font-semibold mb-4">Manage Users</h3>
        <UserTable users={users} />
      </div>

      <div className="flex justify-end mt-6">
        <ActionButton text="Logout" onClick={logout} color="red" />
      </div>
    </div>
  );
};

export default Dashboard;
