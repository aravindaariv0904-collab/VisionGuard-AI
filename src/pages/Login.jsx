import LoginCard from "../components/LoginCard";

export default function Login() {
  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 overflow-hidden">

      {/* Background Glow */}
      <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-cyan-500/20 blur-3xl"></div>

      <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full bg-blue-500/20 blur-3xl"></div>

      <LoginCard />

    </div>
  );
}