import React, { createContext, useState, useEffect, ReactNode } from "react";
import { signInUser, signOutUser, getToken, isAuthenticated } from "../api/authService";
import { jwtDecode } from "jwt-decode";

interface AuthContextType {
  user: any;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any>(null);
  const [authenticated, setAuthenticated] = useState<boolean>(isAuthenticated());
  const [logoutMessage, setLogoutMessage] = useState<string | null>(null); // Logout message state

  useEffect(() => {
    const token = getToken();
    if (token) {
      setAuthenticated(true);
      try {
        const decodedUser = jwtDecode(token);
        setUser(decodedUser);
      } catch {
        setUser(null);
      }
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await signInUser({ email, password });
    setAuthenticated(true);
    const decodedUser = jwtDecode(response.access_token);
    setUser(decodedUser);
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
        setLogoutMessage(null);
      }, 2000); // 2-second delay before resetting auth state
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: authenticated }}>
      {children}
      {logoutMessage && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg">
          {logoutMessage}
        </div>
      )}
    </AuthContext.Provider>
  );
};
