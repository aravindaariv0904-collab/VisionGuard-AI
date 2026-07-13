import { User, Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

export default function SignupCard() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          email, 
          password, 
          full_name: fullName 
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Signup failed");
      }
      setSuccess(data.message || "Account created successfully! You can now log in.");
      // Clear forms
      setFullName("");
      setEmail("");
      setPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md rounded-3xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl p-10">
      <h2 className="text-center text-cyan-400 text-2xl font-bold mb-3">
        VisionGuard AI
      </h2>

      <h1 className="text-4xl font-bold text-center text-white">
        Create Account
      </h1>

      <p className="text-center text-slate-300 mt-3 mb-4">
        Join VisionGuard AI and start detecting AI-generated images.
      </p>

      {error && (
        <div className="p-3 mb-4 rounded-xl bg-red-500/20 border border-red-500/50 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {success && (
        <div className="p-3 mb-4 rounded-xl bg-green-500/20 border border-green-500/50 text-green-200 text-sm text-center">
          {success}
        </div>
      )}

      <form onSubmit={handleSignup}>
        {/* Full Name */}
        <div className="mt-4 flex items-center rounded-xl border border-slate-700 px-4 py-3 focus-within:border-cyan-400 transition-all duration-300">
          <User className="text-cyan-400"/>
          <input
            type="text"
            placeholder="Full Name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="ml-3 w-full bg-transparent outline-none text-white"
            required
          />
        </div>

        {/* Email */}
        <div className="mt-5 flex items-center rounded-xl border border-slate-700 px-4 py-3 focus-within:border-cyan-400 transition-all duration-300">
          <Mail className="text-cyan-400"/>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="ml-3 w-full bg-transparent outline-none text-white"
            required
          />
        </div>

        {/* Password */}
        <div className="mt-5 flex items-center rounded-xl border border-slate-700 px-4 py-3 focus-within:border-cyan-400 transition-all duration-300">
          <Lock className="text-cyan-400"/>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="ml-3 w-full bg-transparent outline-none text-white"
            required
            minLength={6}
          />
          {showPassword ? (
            <EyeOff
              className="cursor-pointer text-slate-400"
              onClick={() => setShowPassword(false)}
            />
          ) : (
            <Eye
              className="cursor-pointer text-slate-400"
              onClick={() => setShowPassword(true)}
            />
          )}
        </div>

        {/* Confirm Password */}
        <div className="mt-5 flex items-center rounded-xl border border-slate-700 px-4 py-3 focus-within:border-cyan-400 transition-all duration-300">
          <Lock className="text-cyan-400"/>
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="ml-3 w-full bg-transparent outline-none text-white"
            required
          />
        </div>

        {/* Checkbox */}
        <label className="mt-5 flex items-center text-slate-300 text-sm cursor-pointer">
          <input type="checkbox" className="mr-2" required/>
          I agree to the Terms & Privacy Policy
        </label>

        {/* Button */}
        <button 
          type="submit"
          disabled={loading}
          className="mt-8 w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3 font-semibold hover:scale-105 transition disabled:opacity-50 text-white"
        >
          {loading ? "Creating Account..." : "Create Account"}
        </button>
      </form>

      {/* Divider */}
      <div className="flex items-center my-6">
        <div className="flex-1 border-t border-slate-700"></div>
        <span className="mx-4 text-slate-400">
          OR
        </span>
        <div className="flex-1 border-t border-slate-700"></div>
      </div>

      {/* Google */}
      <button className="w-full rounded-xl border border-slate-600 py-3 hover:bg-white/10 transition text-white">
        Continue with Google
      </button>

      {/* Login */}
      <div className="mt-6 text-center">
        <span className="text-slate-300">
          Already have an account?
        </span>
        <Link
          to="/login"
          className="ml-2 text-cyan-400"
        >
          Login
        </Link>
      </div>

      {/* Home */}
      <div className="mt-4 text-center">
        <Link
          to="/"
          className="text-cyan-400"
        >
          ← Back to Home
        </Link>
      </div>
    </div>
  );
}