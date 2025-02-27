import axios from "axios";
import { BASE_URL, getAuthHeaders } from "./config";

/**
 * Fetches a list of users.
 *
 * @returns {Promise<any[]>} The API response.
 * @throws {string} Error message if request fails.
 */
export const fetchUsers = async (): Promise<any[]> => {
  try {
    const response = await axios.get(`${BASE_URL}/api/users`,{ headers: getAuthHeaders() }); // Include the Authorization header
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
        throw error.response?.data?.detail || "Failed to fetch users";
    }
    throw new Error("An unexpected error occurred");
  }
};
