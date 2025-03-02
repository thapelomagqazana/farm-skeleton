import React from "react";

/**
 * Props for ErrorMessage component.
 */
interface ErrorMessageProps {
  message: string;
}

/**
 * ErrorMessage
 * Displays an error message in a styled box.
 *
 * @param {ErrorMessageProps} props - The error message to display.
 * @returns {JSX.Element} Error message component.
 */
const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => (
  <div className="bg-red-100 text-red-700 p-4 rounded-md shadow">
    <strong>Error:</strong> {message}
  </div>
);

export default ErrorMessage;
