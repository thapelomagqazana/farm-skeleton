import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { registerUser } from "../api/authService";
import InputField from "../components/InputField";
import Button from "../components/Button";
import { useNavigate } from "react-router-dom";

/**
 * Validation schema for the registration form.
 */
const schema = yup.object().shape({
  name: yup.string().min(3, "Name must be at least 3 characters").required("Name is required"),
  email: yup.string().email("Invalid email format").required("Email is required"),
  password: yup
    .string()
    .min(6, "Password must be at least 6 characters")
    .matches(/[A-Za-z]/, "Must contain letters")
    .matches(/\d/, "Must contain numbers")
    .matches(/\W/, "Must contain a special character")
    .required("Password is required"),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref("password")], "Passwords must match")
    .required("Confirm password is required"),
});

/**
 * Register page for new users.
 *
 * @returns {JSX.Element} The registration form.
 */
const Register: React.FC = () => {
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // React Hook Form setup
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: yupResolver(schema),
  });

  /**
   * Handles form submission and registers the user.
   *
   * @param {Object} data - Form data containing name, email, password, and confirmPassword.
   */
  const onSubmit = async (data: any) => {
    try {
      await registerUser({ name: data.name, email: data.email, password: data.password });
      navigate("/signin"); // Redirect to login on success
    } catch (error) {
      setErrorMessage(error.message || "Registration failed.");
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="bg-white shadow-md rounded-lg p-6 w-96">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Register</h2>
        {errorMessage && <p className="text-red-500 text-sm">{errorMessage}</p>}
        <form onSubmit={handleSubmit(onSubmit)}>
          <InputField label="Name" type="text" name="name" placeholder="Enter your name" register={register} error={errors.name?.message} />
          <InputField label="Email" type="email" name="email" placeholder="Enter your email" register={register} error={errors.email?.message} />

          {/* Password Input with Toggle Visibility */}
          <div className="relative">
            <InputField
              label="Password"
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Enter your password"
              register={register}
              error={errors.password?.message}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-9 text-gray-500 hover:text-gray-700"
            >
              {showPassword ? "🙈" : "👁️"}
            </button>
          </div>

          {/* Confirm Password Input */}
          <div className="relative">
            <InputField
              label="Confirm Password"
              type={showPassword ? "text" : "password"}
              name="confirmPassword"
              placeholder="Confirm your password"
              register={register}
              error={errors.confirmPassword?.message}
            />
          </div>

          <Button text="Register" type="submit" isLoading={isSubmitting} />
        </form>
        <p className="mt-4 text-gray-600 text-sm">
          Already have an account? <a href="/login" className="text-blue-600 hover:underline">Sign in</a>
        </p>
      </div>
    </div>
  );
};

export default Register;
