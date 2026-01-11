"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name || undefined,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Registration failed");
      }

      router.push("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-trace-500/10 border border-trace-500/30 mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-trace-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
            />
          </svg>
        </div>
        <h1 className="text-2xl font-mono font-semibold text-silkscreen">
          Create Account
        </h1>
        <p className="text-substrate-400 mt-2 font-mono text-sm">
          Join the engineering community
        </p>
      </div>

      {/* Form Card */}
      <div className="bg-substrate-900/50 backdrop-blur-sm border border-substrate-800 rounded-lg p-8 shadow-trace">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-mono">
              {error}
            </div>
          )}

          {/* Name Field (Optional) */}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-mono text-substrate-300 mb-2"
            >
              Name{" "}
              <span className="text-substrate-500">(optional)</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full px-4 py-3 bg-substrate-950 border border-substrate-700 rounded-md text-silkscreen font-mono text-sm placeholder-substrate-500 focus:outline-none focus:ring-2 focus:ring-trace-500 focus:border-transparent transition-all"
              placeholder="Ada Lovelace"
            />
          </div>

          {/* Email Field */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-mono text-substrate-300 mb-2"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 bg-substrate-950 border border-substrate-700 rounded-md text-silkscreen font-mono text-sm placeholder-substrate-500 focus:outline-none focus:ring-2 focus:ring-trace-500 focus:border-transparent transition-all"
              placeholder="engineer@example.com"
            />
          </div>

          {/* Password Field */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-mono text-substrate-300 mb-2"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className="w-full px-4 py-3 bg-substrate-950 border border-substrate-700 rounded-md text-silkscreen font-mono text-sm placeholder-substrate-500 focus:outline-none focus:ring-2 focus:ring-trace-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
            <p className="mt-1.5 text-xs font-mono text-substrate-500">
              Must be at least 8 characters
            </p>
          </div>

          {/* Confirm Password Field */}
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-mono text-substrate-300 mb-2"
            >
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 bg-substrate-950 border border-substrate-700 rounded-md text-silkscreen font-mono text-sm placeholder-substrate-500 focus:outline-none focus:ring-2 focus:ring-trace-500 focus:border-transparent transition-all"
              placeholder="••••••••"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-trace-500 hover:bg-trace-600 disabled:bg-trace-500/50 disabled:cursor-not-allowed text-substrate-950 font-mono font-semibold rounded-md transition-all focus:outline-none focus:ring-2 focus:ring-trace-500 focus:ring-offset-2 focus:ring-offset-substrate-900 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Creating account...</span>
              </>
            ) : (
              <span>Create Account</span>
            )}
          </button>
        </form>

        {/* Login Link */}
        <div className="mt-6 text-center">
          <p className="text-substrate-400 font-mono text-sm">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-trace-500 hover:text-trace-400 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>

      {/* Decorative element */}
      <div className="mt-8 flex items-center justify-center gap-2">
        <div className="h-px w-8 bg-substrate-700" />
        <div className="h-2 w-2 rounded-full bg-trace-500/50" />
        <div className="h-px w-8 bg-substrate-700" />
      </div>
    </div>
  );
}
