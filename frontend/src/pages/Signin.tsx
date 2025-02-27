import React, { useState, useContext } from "react";
import { useForm, SubmitHandler } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { AuthContext } from "../context/AuthContext";
import InputField from "../components/InputField";
import Button from "../components/Button";
import { useNavigate } from "react-router-dom";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

/**
 * Validation schema for the sign-in form.
 */
const schema = yup.object().shape({
  email: yup.string().email("Invalid email format").required("Email is required"),
  password: yup.string().min(6, "Password must be at least 6 characters").required("Password is required"),
});

/**
 * Interface for form inputs.
 */
interface SignInFormInputs {
  email: string;
  password: string;
}

/**
 * Sign-in page for users.
 *
 * @returns {JSX.Element} The sign-in form.
 */
const Signin: React.FC = () => {
  const navigate = useNavigate();
  const authContext = useContext(AuthContext);
  const [showPassword, setShowPassword] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string>("");
  const [snackbarSeverity, setSnackbarSeverity] = useState<"success" | "error">("success");

  // React Hook Form setup
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignInFormInputs>({
    resolver: yupResolver(schema),
  });

  /**
   * Handles form submission and signs in the user.
   */
  const onSubmit: SubmitHandler<SignInFormInputs> = async (data) => {
    try {
      await authContext?.login(data.email, data.password);

      // Show success snackbar
      setSnackbarMessage("Sign-in successful! Redirecting...");
      setSnackbarSeverity("success");
      setOpenSnackbar(true);

      // Redirect to dashboard
      setTimeout(() => {
        navigate("/dashboard");
      }, 2000);
    } catch (error: any) {
      setSnackbarMessage(error.response?.data?.detail || "Invalid email or password.");
      setSnackbarSeverity("error");
      setOpenSnackbar(true);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="bg-white shadow-md rounded-lg p-6 w-96 mt-10">
        <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">Sign In</h2>

        <form onSubmit={handleSubmit(onSubmit)}>
          <InputField
            label="Email"
            type="email"
            name="email"
            placeholder="Enter your email"
            register={register}
            error={errors.email?.message}
          />

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

          <Button text="Sign In" type="submit" isLoading={isSubmitting} />
        </form>

        {/* Forgot Password Link */}
        <p className="mt-2 text-gray-600 text-sm text-center">
          <a href="/forgot-password" className="text-blue-600 hover:underline">Forgot password?</a>
        </p>

        {/* Redirect Link */}
        <p className="mt-4 text-gray-600 text-sm text-center">
          Don't have an account? <a href="/register" className="text-blue-600 hover:underline">Register</a>
        </p>
      </div>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={3000}
        onClose={() => setOpenSnackbar(false)}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <MuiAlert elevation={6} variant="filled" severity={snackbarSeverity} onClose={() => setOpenSnackbar(false)}>
          {snackbarMessage}
        </MuiAlert>
      </Snackbar>
    </div>
  );
};

export default Signin;
