import { useState } from "react";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Link } from "react-router-dom";

export default function LoginCard() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  return (
    <div className="w-full max-w-md rounded-3xl bg-white/10 backdrop-blur-2xl border border-white/20 shadow-2xl p-10">
      <h2 className="text-center text-cyan-400 text-2xl font-bold mb-4">
        VisionGuard AI
      </h2>
      <h1 className="text-4xl font-bold text-center text-white">
        Welcome Back 👋
      </h1>

      <p className="text-center text-slate-300 mt-3">
        Sign in to continue using VisionGuard AI
      </p>

      <div className="mt-8">

        <label className="text-slate-300">
          Email
        </label>

        <div className="mt-2 flex items-center rounded-xl border border-slate-700 focus-within:border-cyan-400 transition-all duration-300 px-4 py-3">

          <Mail className="text-cyan-400" size={20}/>

          <input
         type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="ml-3 w-full bg-transparent outline-none text-white"
      />

        </div>

      </div>

      <div className="mt-6">

        <label className="text-slate-300">
          Password
        </label>

        <div className="mt-2 flex items-center rounded-xl border border-slate-700 focus-within:border-cyan-400 transition-all duration-300 px-4 py-3">

          <Lock className="text-cyan-400" size={20}/>

          <input
         type={showPassword ? "text" : "password"}
         placeholder="Enter password"
         value={password}
         onChange={(e) => setPassword(e.target.value)}
         className="ml-3 w-full bg-transparent outline-none text-white"
/>

          {showPassword ? (
        <EyeOff
        className="text-slate-400 cursor-pointer"
        onClick={() => setShowPassword(false)}
       />
       ) : (
       <Eye
       className="text-slate-400 cursor-pointer"
       onClick={() => setShowPassword(true)}
       />
       )}

        </div>

      </div>

      <div className="mt-5 flex justify-between text-sm">

        <label className="text-slate-300">
          <input type="checkbox" className="mr-2"/>
          Remember Me
        </label>

        <a href="#" className="text-cyan-400 hover:text-cyan-300">
          Forgot Password?
        </a>

      </div>

      <button className="mt-8 w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3 text-lg font-semibold shadow-lg hover:scale-105 hover:shadow-cyan-500/40 transition-all duration-300 text-white">
        Login
      </button>
      <div className="flex items-center my-6">
        <div className="flex-1 border-t border-slate-700"></div>

        <span className="px-4 text-slate-400">
          OR
        </span>

        <div className="flex-1 border-t border-slate-700"></div>
      </div>
      <button className="w-full rounded-xl border border-slate-600 py-3 hover:bg-white/10 transition text-white">
        Continue with Google
      </button>
      <div className="mt-6 text-center text-slate-300">
        Don't have an account?

        <span className="text-cyan-400 cursor-pointer ml-2">
          <Link to="/signup" className="text-cyan-400">
            Sign Up
          </Link>
        </span>

      </div>

    </div>
  );
}