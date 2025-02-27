import axios from "axios";
import { BASE_URL } from "./config";

/**
 * Registers a new user.
 *
 * @param {Object} data - User registration data (name, email, password).
 * @returns {Promise<any>} The API response.
 * @throws {string} Error message if registration fails.
 */
export const registerUser = async (data: { name: string; email: string; password: string }) => {
  try {
    const response = await axios.post(`${BASE_URL}/api/users`, data);
    return response.data;
  } catch (error: any) {
    throw error.response?.data?.detail || "Registration failed";
  }
};
