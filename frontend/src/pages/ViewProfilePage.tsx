import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getUserProfile } from "../api/userService";
import ProfileCard from "../components/profile/ProfileCard";
import Spinner from "../components/Spinner";
import ErrorMessage from "../components/ErrorMessage";

/**
 * ViewProfilePage
 * Displays the authenticated user's profile.
 *
 * @returns {JSX.Element} The user's profile page.
 */
const ViewProfilePage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  /**
   * Fetch the user's profile on component mount.
   */
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        if (userId) {
          const data = await getUserProfile(userId);
          setProfile(data);
        } else {
          setError("User not authenticated.");
        }
      } catch (err: any) {
        setError(err.message || "Failed to fetch profile.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId]);

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      {loading ? (
        <Spinner />
      ) : error ? (
        <ErrorMessage message={error} />
      ) : profile ? (
        <ProfileCard profile={profile} />
      ) : (
        <ErrorMessage message="No profile data available." />
      )}
    </div>
  );
};

export default ViewProfilePage;
