import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import UploadBox from "../components/UploadBox";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white">
      <Navbar />
      <Hero />
      <UploadBox />
    </div>
  );
}