import React, { createContext, useState, useEffect, ReactNode } from "react";
import { signInUser, signOutUser, getToken, isAuthenticated } from "../api/authService";
import { jwtDecode } from "jwt-decode";

interface AuthContextType {
  user: any;
  userId: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

// Define the user structure from the JWT payload
interface DecodedUser {
  sub: string; // Email or User ID
  exp: number; // Expiration timestamp
  [key: string]: any; // Additional payload properties
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any>(null);
  const [userId, setUserId] = useState<any>(null); // Store userId separately
  const [authenticated, setAuthenticated] = useState<boolean>(isAuthenticated());
  const [logoutMessage, setLogoutMessage] = useState<string | null>(null); // Logout message state

  useEffect(() => {
    const token = getToken();
    if (token) {
      try {
        const decodedUser: DecodedUser = jwtDecode(token);
        setUser(decodedUser);
        setUserId(decodedUser.sub); // Extract userId from `sub`
        setAuthenticated(true);

        // Check if token has expired
        if (decodedUser.exp * 1000 < Date.now()) {
          handleTokenExpiration();
        }
      } catch {
        setUser(null);
        setUserId(null);
        setAuthenticated(false);
      }
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await signInUser({ email, password });
    setAuthenticated(true);
    const decodedUser = jwtDecode(response.access_token);
    setUser(decodedUser);
    setUserId(decodedUser.sub); // Store the user ID
  };

  /**
   * Handles user logout with a slight delay for better UX.
   */
  const logout = async () => {
    try {
      await signOutUser();
      setLogoutMessage("You have been logged out successfully.");
      
      setTimeout(() => {
        setAuthenticated(false);
        setUser(null);
        setUserId(null);
        setLogoutMessage(null);
      }, 2000); // 2-second delay before resetting auth state
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  /**
   * Handles token expiration by logging out the user and redirecting to sign-in.
   */
  const handleTokenExpiration = () => {
    localStorage.removeItem("accessToken");
    setAuthenticated(false);
    setUser(null);
    setUserId(null);
  };

  return (
    <AuthContext.Provider value={{ user, userId, login, logout, isAuthenticated: authenticated }}>
      {children}
      {logoutMessage && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg">
          {logoutMessage}
        </div>
      )}
    </AuthContext.Provider>
  );
};
