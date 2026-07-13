import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const userJson = localStorage.getItem("user");
  const user = userJson ? JSON.parse(userJson) : null;

  const handleLogout = async () => {
    try {
      // Call API logout (fire and forget or catch errors)
      await fetch("http://localhost:8000/auth/logout", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
    } catch (err) {
      console.warn("API logout failed:", err);
    }
    
    // Clear credentials
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav className="flex items-center justify-between px-10 py-6">
      <Link to="/">
        <h1 className="text-3xl font-bold text-cyan-400 cursor-pointer hover:text-cyan-300 transition">
          VisionGuard AI
        </h1>
      </Link>

      <div className="flex items-center gap-6">
        {token && user ? (
          <>
            <span className="text-slate-300 text-sm font-semibold">
              Hello, <span className="text-cyan-400">{user.full_name || user.email}</span>
            </span>
            <button 
              onClick={handleLogout}
              className="border border-cyan-500 hover:bg-cyan-500/10 text-cyan-400 px-6 py-2 rounded-xl font-semibold transition"
            >
              Logout
            </button>
          </>
        ) : (
          <Link to="/login">
            <button className="bg-cyan-500 hover:bg-cyan-600 px-6 py-2 rounded-xl font-semibold transition text-white">
              Login
            </button>
          </Link>
        )}
      </div>
    </nav>
  );
}