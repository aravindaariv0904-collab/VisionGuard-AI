import { useState } from "react";
import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import UploadBox from "../components/UploadBox";
import { Sparkles, ArrowLeft, Cpu, Clock, CheckCircle, AlertTriangle } from "lucide-react";

export default function LandingPage() {
  const [result, setResult] = useState(null);

  const handleResult = (data) => {
    setResult(data);
  };

  const handleReset = () => {
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white pb-20">
      <Navbar />

      {!result ? (
        <>
          <Hero />
          <UploadBox onResult={handleResult} />
        </>
      ) : (
        <div className="mt-10 max-w-5xl mx-auto px-6">
          {/* Header Action */}
          <button 
            onClick={handleReset}
            className="flex items-center gap-2 text-slate-400 hover:text-cyan-400 transition mb-6 font-semibold"
          >
            <ArrowLeft size={20} />
            Back to Upload
          </button>

          {/* Results Card */}
          <div className="rounded-3xl bg-white/5 border border-white/10 p-8 backdrop-blur-2xl shadow-2xl">
            <div className="flex flex-col md:flex-row gap-8 items-center justify-center">
              
              {/* Overlay / Heatmap Visual comparison */}
              <div className="w-full md:w-1/2 flex flex-col items-center">
                <h3 className="text-lg font-semibold text-slate-300 mb-3 flex items-center gap-2">
                  <Sparkles size={16} className="text-cyan-400" />
                  Grad-CAM Heatmap Analysis
                </h3>
                <div className="relative group rounded-2xl overflow-hidden border border-slate-700 bg-black/40 aspect-square w-full flex items-center justify-center max-h-[400px]">
                  {/* Toggle between showing heatmap overlay or heatmap raw, or just showing overlay */}
                  <img 
                    src={result.overlay_url} 
                    alt="Analysis Overlay"
                    className="w-full h-full object-contain"
                  />
                </div>
                <p className="mt-3 text-sm text-slate-400 text-center">
                  Brighter regions represent areas of higher AI-generation suspicion.
                </p>
              </div>

              {/* Data & Decision details */}
              <div className="w-full md:w-1/2 flex flex-col justify-center">
                
                <span className="text-xs uppercase tracking-widest text-cyan-400 font-bold">
                  Authentication Result
                </span>

                <h2 className="mt-2 text-4xl font-extrabold flex items-center gap-3">
                  {result.prediction}
                  {result.prediction === "Real" ? (
                    <CheckCircle className="text-green-400" size={32} />
                  ) : (
                    <AlertTriangle className="text-rose-400" size={32} />
                  )}
                </h2>

                {/* Score slider */}
                <div className="mt-6">
                  <div className="flex justify-between text-sm font-semibold mb-1">
                    <span className="text-slate-300">Detection Confidence</span>
                    <span className={result.prediction === "Real" ? "text-green-400" : "text-rose-400"}>
                      {result.confidence.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-1000 ${
                        result.prediction === "Real" ? "bg-gradient-to-r from-green-500 to-cyan-500" : "bg-gradient-to-r from-rose-500 to-amber-500"
                      }`}
                      style={{ width: `${result.confidence}%` }}
                    ></div>
                  </div>
                </div>

                {/* Metrics grid */}
                <div className="mt-8 grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-white/5 border border-white/5 flex items-center gap-3">
                    <Clock className="text-cyan-400" size={24} />
                    <div>
                      <div className="text-xs text-slate-400 font-semibold uppercase">Processing Time</div>
                      <div className="text-lg font-bold text-white">{result.processing_time}s</div>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-white/5 border border-white/5 flex items-center gap-3">
                    <Cpu className="text-cyan-400" size={24} />
                    <div>
                      <div className="text-xs text-slate-400 font-semibold uppercase">Model Version</div>
                      <div className="text-lg font-bold text-white">v{result.model_version}</div>
                    </div>
                  </div>
                </div>

                {/* Action button */}
                <div className="mt-8 flex gap-4">
                  <button 
                    onClick={handleReset}
                    className="w-full rounded-xl bg-cyan-500 hover:bg-cyan-600 px-6 py-4 font-semibold text-lg transition text-center shadow-lg shadow-cyan-500/20"
                  >
                    Scan Another Image
                  </button>
                </div>

              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}