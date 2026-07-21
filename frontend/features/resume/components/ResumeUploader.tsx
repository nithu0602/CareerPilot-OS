"use client";

import { useRef, useState } from "react";
import { Upload, FileText, CheckCircle2 } from "lucide-react";

export function ResumeUploader() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setSelectedFile(file);
  };

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  return (
    <section
      onClick={openFilePicker}
      className="
        cursor-pointer
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
      "
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx"
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="flex flex-col items-center text-center">
        <div className="mb-6 rounded-full bg-teal-500/10 p-5">
          <Upload className="h-10 w-10 text-teal-400" />
        </div>

        <h2 className="text-2xl font-semibold text-white">
          Upload Your Resume
        </h2>

        <p className="mt-3 max-w-lg text-slate-400">
          Drag & drop your resume here or click below to browse.
        </p>

        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            openFilePicker();
          }}
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
          {selectedFile ? "Replace Resume" : "Choose File"}
        </button>

        {selectedFile ? (
          <div className="mt-8 w-full max-w-lg rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-6 w-6 text-emerald-400" />

              <div className="text-left">
                <p className="font-medium text-white">
                  {selectedFile.name}
                </p>

                <p className="text-sm text-slate-400">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-8 flex items-center gap-2 text-sm text-slate-500">
            <FileText className="h-4 w-4" />
            <span>Supported formats: PDF, DOCX (Max 5 MB)</span>
          </div>
        )}
      </div>
    </section>
  );
}