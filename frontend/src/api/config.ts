import { getToken } from "./authService";

/**
 * API Configuration - Base URL and Headers
 */
export const BASE_URL = import.meta.env.VITE_API_URL;

/**
 * Retrieves authentication headers for requests.
 * @returns Object containing the Authorization header with Bearer token.
 */
/**
 * Retrieves the authentication headers for requests.
 * @returns {Object} The authorization headers with the Bearer token.
 */
export const getAuthHeaders = () => {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
};
