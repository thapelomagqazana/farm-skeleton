import React from "react";

/**
 * Props for Button component.
 */
interface ButtonProps {
  text: string;
  type?: "button" | "submit";
  onClick?: () => void;
  isLoading?: boolean;
}

/**
 * A reusable button component.
 *
 * @param {ButtonProps} props - Button properties including text, type, click handler, and loading state.
 * @returns {JSX.Element} A styled button.
 */
const Button: React.FC<ButtonProps> = ({ text, type = "button", onClick, isLoading }) => {
  return (
    <button
      type={type}
      onClick={onClick}
      className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
      disabled={isLoading}
    >
      {isLoading ? "Loading..." : text}
    </button>
  );
};

export default Button;
