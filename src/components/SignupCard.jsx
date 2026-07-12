import { User, Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";

export default function SignupCard() {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="w-full max-w-md rounded-3xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl p-10">

      <h2 className="text-center text-cyan-400 text-2xl font-bold mb-3">
        VisionGuard AI
      </h2>

      <h1 className="text-4xl font-bold text-center text-white">
        Create Account
      </h1>

      <p className="text-center text-slate-300 mt-3">
        Join VisionGuard AI and start detecting AI-generated images.
      </p>

      {/* Full Name */}

      <div className="mt-8 flex items-center rounded-xl border border-slate-700 px-4 py-3">
        <User className="text-cyan-400"/>
        <input
          type="text"
          placeholder="Full Name"
          className="ml-3 w-full bg-transparent outline-none text-white"
        />
      </div>

      {/* Email */}

      <div className="mt-5 flex items-center rounded-xl border border-slate-700 px-4 py-3">
        <Mail className="text-cyan-400"/>
        <input
          type="email"
          placeholder="Email"
          className="ml-3 w-full bg-transparent outline-none text-white"
        />
      </div>

      {/* Password */}

      <div className="mt-5 flex items-center rounded-xl border border-slate-700 px-4 py-3">
        <Lock className="text-cyan-400"/>

        <input
          type={showPassword ? "text" : "password"}
          placeholder="Password"
          className="ml-3 w-full bg-transparent outline-none text-white"
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

      <div className="mt-5 flex items-center rounded-xl border border-slate-700 px-4 py-3">
        <Lock className="text-cyan-400"/>

        <input
          type={showPassword ? "text" : "password"}
          placeholder="Confirm Password"
          className="ml-3 w-full bg-transparent outline-none text-white"
        />
      </div>

      {/* Checkbox */}

      <label className="mt-5 flex items-center text-slate-300 text-sm">
        <input type="checkbox" className="mr-2"/>
        I agree to the Terms & Privacy Policy
      </label>

      {/* Button */}

      <button className="mt-8 w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3 font-semibold hover:scale-105 transition">
        Create Account
      </button>

      {/* Divider */}

      <div className="flex items-center my-6">
        <div className="flex-1 border-t border-slate-700"></div>

        <span className="mx-4 text-slate-400">
          OR
        </span>

        <div className="flex-1 border-t border-slate-700"></div>
      </div>

      {/* Google */}

      <button className="w-full rounded-xl border border-slate-600 py-3 hover:bg-white/10 transition">
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