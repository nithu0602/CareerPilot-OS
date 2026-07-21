"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useRef, useState, type ChangeEvent } from "react";
import { Upload, FileText, CheckCircle2 } from "lucide-react";
import { AnalysisErrorCard } from "@/features/dashboard/components/analysis-error-card";
import { AnalysisLoadingScreen, type AnalysisPhase } from "@/features/dashboard/components/analysis-loading-screen";
import { logger } from "@/lib/logger";
import { analyzeDashboard, dashboardQueryKey, uploadResume } from "@/services/careerpilot-api";
import type { DashboardAnalysis } from "@/types";

const maximumFileSizeBytes = 5 * 1024 * 1024;
const acceptedFileTypes = new Set(["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]);

export function ResumeUploader() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [phase, setPhase] = useState<AnalysisPhase>("uploading");
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const router = useRouter();
  const queryClient = useQueryClient();

  const analysisMutation = useMutation<DashboardAnalysis, Error, File>({
    mutationFn: async (file) => {
      setPhase("uploading");
      const upload = await uploadResume(file);
      if (!upload.raw_text.trim()) {
        throw new Error("We could not extract readable text from this resume. Please choose another PDF or DOCX file.");
      }

      setPhase("analyzing");
      return analyzeDashboard(upload.raw_text);
    },
    onSuccess: (analysis) => {
      queryClient.setQueryData(dashboardQueryKey, analysis);
      router.push("/dashboard");
    },
    onError: (error) => {
      logger.error("resume_analysis_failed", { message: error.message });
    },
  });

  const startAnalysis = (file: File) => {
    if (file.size > maximumFileSizeBytes) {
      setValidationMessage("This file is larger than 5 MB. Please choose a smaller PDF or DOCX resume.");
      return;
    }
    if (!acceptedFileTypes.has(file.type) && !/\.(pdf|docx)$/i.test(file.name)) {
      setValidationMessage("Please choose a PDF or DOCX resume.");
      return;
    }

    setSelectedFile(file);
    setValidationMessage(null);
    analysisMutation.reset();
    analysisMutation.mutate(file);
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (file) startAnalysis(file);
  };

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  if (analysisMutation.isPending) {
    return <AnalysisLoadingScreen phase={phase} />;
  }

  const errorMessage = validationMessage ?? analysisMutation.error?.message;
  if (errorMessage) {
    return (
      <AnalysisErrorCard
        message={errorMessage}
        onRetry={() => selectedFile && startAnalysis(selectedFile)}
        retryDisabled={!selectedFile}
      />
    );
  }

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
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
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
          Choose your resume and we&apos;ll automatically create your dashboard.
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
