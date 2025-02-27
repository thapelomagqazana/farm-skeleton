import React from "react";

/**
 * Props for InputField component.
 */
interface InputFieldProps {
  label: string;
  type: string;
  name: string;
  placeholder: string;
  register: any;
  error?: string;
}

/**
 * A reusable input field component.
 *
 * @param {InputFieldProps} props - Input properties including label, type, name, placeholder, register, and error message.
 * @returns {JSX.Element} A styled input field.
 */
const InputField: React.FC<InputFieldProps> = ({ label, type, name, placeholder, register, error }) => {
  return (
    <div className="mb-4">
      <label htmlFor={name} className="block text-gray-700 font-medium mb-2">
        {label}
      </label>
      <input
        id={name}
        type={type}
        {...register(name)}
        placeholder={placeholder}
        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
};

export default InputField;
