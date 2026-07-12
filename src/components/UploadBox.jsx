import { Upload } from "lucide-react";

export default function UploadBox() {
  return (
    <div className="mt-16 flex justify-center">
      <div className="w-full max-w-3xl rounded-3xl border-2 border-dashed border-cyan-500 bg-white/5 p-12 backdrop-blur-xl transition hover:border-cyan-300">

        <Upload className="mx-auto text-cyan-400" size={70} />

        <h2 className="mt-6 text-center text-3xl font-bold">
          Drag & Drop Image
        </h2>

        <p className="mt-2 text-center text-slate-300">
          OR
        </p>

        <div className="mt-6 flex justify-center">
          <button className="rounded-xl bg-cyan-500 px-8 py-4 text-lg font-semibold hover:bg-cyan-600">
            Upload Image
          </button>
        </div>

        <p className="mt-6 text-center text-slate-400">
          Supports JPG • PNG • WEBP
        </p>

      </div>
    </div>
  );
}