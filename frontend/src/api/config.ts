/**
 * API Configuration - Base URL and Headers
 */
export const BASE_URL = import.meta.env.VITE_API_URL;

/**
 * Retrieves authentication headers for requests.
 * @returns Object containing the Authorization header with Bearer token.
 */
export const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    headers: { Authorization: `Bearer ${token}` },
  };
};
