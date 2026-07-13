import { useState } from "react";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export default function LoginCard() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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

      {error && (
        <div className="mt-4 p-3 rounded-xl bg-red-500/20 border border-red-500/50 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleLogin}>
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
              required
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
              required
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
          <label className="text-slate-300 cursor-pointer">
            <input type="checkbox" className="mr-2"/>
            Remember Me
          </label>
          <a href="#" className="text-cyan-400 hover:text-cyan-300">
            Forgot Password?
          </a>
        </div>

        <button 
          type="submit"
          disabled={loading}
          className="mt-8 w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-3 text-lg font-semibold shadow-lg hover:scale-105 hover:shadow-cyan-500/40 transition-all duration-300 text-white disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

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