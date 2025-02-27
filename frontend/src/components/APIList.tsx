import React from "react";

const APIList: React.FC = () => {
  return (
    <div className="overflow-x-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">API Endpoints</h2>
      
      <h3 className="text-xl font-semibold text-gray-700 mt-4">User CRUD</h3>
      <table className="w-full border-collapse border border-gray-300 mt-2">
        <thead className="bg-gray-200">
          <tr>
            <th className="border p-2">Operation</th>
            <th className="border p-2">API Route</th>
            <th className="border p-2">Method</th>
          </tr>
        </thead>
        <tbody>
          {[
            ["Create User", "/api/users", "POST"],
            ["List Users", "/api/users", "GET"],
            ["Get User", "/api/users/{id}", "GET"],
            ["Update User", "/api/users/{id}", "PUT"],
            ["Delete User", "/api/users/{id}", "DELETE"],
          ].map(([operation, route, method], index) => (
            <tr key={index} className="text-center">
              <td className="border p-2">{operation}</td>
              <td className="border p-2">{route}</td>
              <td className="border p-2 font-semibold">{method}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 className="text-xl font-semibold text-gray-700 mt-4">Authentication</h3>
      <table className="w-full border-collapse border border-gray-300 mt-2">
        <thead className="bg-gray-200">
          <tr>
            <th className="border p-2">Operation</th>
            <th className="border p-2">API Route</th>
            <th className="border p-2">Method</th>
          </tr>
        </thead>
        <tbody>
          {[
            ["Sign-in", "/auth/signin", "POST"],
            ["Sign-out", "/auth/signout", "POST"],
          ].map(([operation, route, method], index) => (
            <tr key={index} className="text-center">
              <td className="border p-2">{operation}</td>
              <td className="border p-2">{route}</td>
              <td className="border p-2 font-semibold">{method}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default APIList;
