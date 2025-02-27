import React from "react";

interface DashboardCardProps {
  title: string;
  value: string | number;
}

/**
 * Displays a summary card for the dashboard.
 *
 * @param {DashboardCardProps} props - Component props.
 * @returns {JSX.Element} Dashboard summary card.
 */
const DashboardCard: React.FC<DashboardCardProps> = ({ title, value }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h4 className="text-lg font-semibold text-gray-700">{title}</h4>
      <p className="text-2xl font-bold text-blue-600">{value}</p>
    </div>
  );
};

export default DashboardCard;
