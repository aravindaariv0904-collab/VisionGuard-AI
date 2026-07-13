import { useState, useRef } from "react";
import { Upload, Loader2, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function UploadBox({ onResult }) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadFile(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      uploadFile(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const uploadFile = async (file) => {
    // Basic file validation
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!allowedTypes.includes(file.type)) {
      setError("Invalid file format. Only JPG, PNG, and WEBP are supported.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("File is too large. Max size is 10MB.");
      return;
    }

    setError("");
    setLoading(true);

    const token = localStorage.getItem("token");
    if (!token) {
      setError("Please log in to analyze images.");
      setLoading(false);
      // Optional: redirect to login after a brief delay
      setTimeout(() => {
        navigate("/login");
      }, 1500);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Image analysis failed.");
      }

      onResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-16 flex flex-col items-center justify-center px-4">
      <div 
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={triggerFileInput}
        className="w-full max-w-3xl rounded-3xl border-2 border-dashed border-cyan-500 bg-white/5 p-12 backdrop-blur-xl transition hover:border-cyan-300 cursor-pointer flex flex-col items-center justify-center text-center"
      >
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/jpeg, image/png, image/webp"
          className="hidden" 
        />

        {loading ? (
          <div className="py-6 flex flex-col items-center">
            <Loader2 className="animate-spin text-cyan-400 mb-4" size={70} />
            <h2 className="text-2xl font-bold text-white">Analyzing Image...</h2>
            <p className="mt-2 text-slate-400">Extracting features and generating Grad-CAM heatmaps</p>
          </div>
        ) : (
          <>
            <Upload className="mx-auto text-cyan-400" size={70} />
            <h2 className="mt-6 text-3xl font-bold">
              Drag & Drop Image
            </h2>
            <p className="mt-2 text-slate-300">
              OR
            </p>
            <div className="mt-6 flex justify-center">
              <button 
                type="button"
                className="rounded-xl bg-cyan-500 px-8 py-4 text-lg font-semibold hover:bg-cyan-600 transition"
              >
                Upload Image
              </button>
            </div>
            <p className="mt-6 text-slate-400">
              Supports JPG • PNG • WEBP
            </p>
          </>
        )}
      </div>

      {error && (
        <div className="mt-6 w-full max-w-3xl flex items-center justify-center gap-2 p-4 rounded-2xl bg-red-500/20 border border-red-500/50 text-red-200 text-sm">
          <AlertCircle size={20} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}