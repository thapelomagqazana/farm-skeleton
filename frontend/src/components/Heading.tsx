import React from "react";

/**
 * Props for Heading component.
 */
interface HeadingProps {
  text: string;
}

/**
 * A reusable heading component.
 *
 * @param {HeadingProps} props - Heading properties including text.
 * @returns {JSX.Element} A styled heading component.
 */
const Heading: React.FC<HeadingProps> = ({ text }) => {
  return <h2 className="text-2xl font-bold text-gray-800">{text}</h2>;
};

export default Heading;
