import React from "react";

/**
 * Spinner
 * Shows a loading animation.
 *
 * @returns {JSX.Element} Loading spinner.
 */
const Spinner: React.FC = () => (
  <div className="flex justify-center items-center">
    <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-500"></div>
  </div>
);

export default Spinner;
