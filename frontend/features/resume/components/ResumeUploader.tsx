"use client";
import { useRef } from "react";
import { Upload, FileText } from "lucide-react";

export function ResumeUploader() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  return (
    <section
  onClick={() => fileInputRef.current?.click()}
  className="
    rounded-2xl
    border-2
    border-dashed
    border-slate-700
    bg-slate-900/50
    p-12
    transition-all
    duration-300
    hover:border-teal-400
    hover:bg-slate-900/70
    cursor-pointer
  "
>     <input
  ref={fileInputRef}
  type="file"
  accept=".pdf,.doc,.docx"
  className="hidden"
/>
      <div className="flex flex-col items-center text-center">
        <div className="mb-6 rounded-full bg-teal-500/10 p-5">
          <Upload className="h-10 w-10 text-teal-400" />
        </div>

        <h2 className="text-2xl font-semibold text-white">
          Upload Your Resume
        </h2>

        <p className="mt-3 max-w-lg text-slate-400">
          Drag & drop your resume here or click the button below to browse
          your computer.
        </p>

        <button
          className="
            mt-8
            rounded-xl
            bg-teal-500
            px-6
            py-3
            font-medium
            text-slate-950
            transition
            hover:bg-teal-400
          "
        >
          Choose File
        </button>

        <div className="mt-8 flex items-center gap-2 text-sm text-slate-500">
          <FileText className="h-4 w-4" />
          <span>Supported formats: PDF, DOCX (Max 5 MB)</span>
        </div>
      </div>
    </section>
  );
}