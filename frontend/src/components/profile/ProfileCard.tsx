import React from "react";

/**
 * Props for ProfileCard component.
 */
interface ProfileCardProps {
  profile: {
    name: string;
    email: string;
    role: string;
    created_at: string;
  };
}

/**
 * ProfileCard
 * Displays user profile information in a styled card.
 *
 * @param {ProfileCardProps} props - User profile data.
 * @returns {JSX.Element} The profile card component.
 */
const ProfileCard: React.FC<ProfileCardProps> = ({ profile }) => {
  return (
    <div className="bg-white shadow-md rounded-lg p-6 w-full max-w-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">My Profile</h2>
      <p className="text-gray-600"><strong>Name:</strong> {profile.name}</p>
      <p className="text-gray-600"><strong>Email:</strong> {profile.email}</p>
      {/* <p className="text-gray-600"><strong>Role:</strong> {profile.role}</p> */}
      <p className="text-gray-600"><strong>Joined:</strong> {new Date(profile.created_at).toLocaleDateString()}</p>
    </div>
  );
};

export default ProfileCard;
