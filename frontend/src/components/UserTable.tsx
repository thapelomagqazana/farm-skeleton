import React from "react";

interface User {
  id: string;
  name: string;
  email: string;
}

interface UserTableProps {
  users: User[];
}

/**
 * Displays a table of users.
 *
 * @param {UserTableProps} props - Component props.
 * @returns {JSX.Element} User table.
 */
const UserTable: React.FC<UserTableProps> = ({ users }) => {
  return (
    <div className="overflow-x-auto bg-white shadow-md rounded-lg">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-3 text-left">Name</th>
            <th className="p-3 text-left">Email</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="border-b">
              <td className="p-3">{user.name}</td>
              <td className="p-3">{user.email}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserTable;
