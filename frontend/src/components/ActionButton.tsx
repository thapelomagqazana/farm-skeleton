import React from "react";

interface ActionButtonProps {
  text: string;
  onClick: () => void;
  color?: "blue" | "red";
}

/**
 * A customizable action button.
 *
 * @param {ActionButtonProps} props - Button props.
 * @returns {JSX.Element} Action button.
 */
const ActionButton: React.FC<ActionButtonProps> = ({ text, onClick, color = "blue" }) => {
  const buttonColor = color === "red" ? "bg-red-500 hover:bg-red-700" : "bg-blue-500 hover:bg-blue-700";

  return (
    <button
      onClick={onClick}
      className={`${buttonColor} text-white font-bold py-2 px-4 rounded`}
    >
      {text}
    </button>
  );
};

export default ActionButton;
