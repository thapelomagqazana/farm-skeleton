import axios from "axios";
import { BASE_URL, getAuthHeaders } from "./config";

/**
 * Registers a new user.
 *
 * @param {Object} data - User registration data (name, email, password).
 * @returns {Promise<any>} The API response.
 * @throws {string} Error message if registration fails.
 */
export const registerUser = async (data: { name: string; email: string; password: string }): Promise<any> => {
  try {
    const response = await axios.post(`${BASE_URL}/api/users`, data);
    console.log(response.data);
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      //  Ensure we extract meaningful error messages
      const errorMessage = error.response?.data?.detail || "Registration failed. Please try again.";
      throw errorMessage;
    }
    throw new Error("An unexpected error occurred");
  }
};

/**
 * Signs in an existing user.
 *
 * @param {Object} credentials - User credentials (email, password).
 * @returns {Promise<{ access_token: string; token_type: string }>} The access token and token type.
 * @throws {string} Error message if authentication fails.
 */
export const signInUser = async (credentials: { email: string; password: string }): Promise<{ access_token: string; token_type: string }> => {
    try {
      const response = await axios.post(`${BASE_URL}/auth/signin`, credentials);
      
      // Store JWT token in local storage for authentication
      localStorage.setItem("accessToken", response.data.access_token);
  
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        throw error.response?.data?.detail || "Sign-in failed";
      }
      throw new Error("An unexpected error occurred");
    }
};

/**
 * Signs out the user by removing the JWT token from local storage.
 */
export const signOutUser = async () => {
    try {
        const response = await axios.post(
            `${BASE_URL}/auth/signout`, 
            {}, // Empty body
            { headers: getAuthHeaders() } // Include the Authorization header
        );
        
        localStorage.removeItem("accessToken");
    
        return response.data;
    } catch (error: unknown) {
        if (axios.isAxiosError(error)) {
        throw error.response?.data?.detail || "Sign-out failed";
        }
        throw new Error("An unexpected error occurred");
    }
    
};

/**
 * Retrieves the JWT token from local storage.
 *
 * @returns {string | null} The stored JWT token, or null if not found.
 */
export const getToken = (): string | null => {
    return localStorage.getItem("accessToken");
};

/**
 * Checks if the user is authenticated.
 *
 * @returns {boolean} True if the user has a valid token, otherwise false.
 */
export const isAuthenticated = (): boolean => {
    return !!getToken();
};
