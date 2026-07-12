import { Link } from "react-router-dom";
export default function Navbar() {

  return (
    <nav className="flex items-center justify-between px-10 py-6">

      <h1 className="text-3xl font-bold text-cyan-400">
        VisionGuard AI
      </h1>

      <Link to="/login">
  <button className="bg-cyan-500 hover:bg-cyan-600 px-6 py-2 rounded-xl font-semibold transition">
    Login
  </button>
</Link> 

    </nav>
  );
}