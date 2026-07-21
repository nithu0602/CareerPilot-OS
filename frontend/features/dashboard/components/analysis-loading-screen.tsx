"use client";

import { motion } from "framer-motion";
import { FileSearch, LoaderCircle, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, Progress } from "@/components/ui/primitives";

export type AnalysisPhase = "uploading" | "analyzing";

const phaseDetails: Record<AnalysisPhase, { label: string; description: string; target: number }> = {
  uploading: {
    label: "Reading your resume",
    description: "Extracting text and validating your document.",
    target: 42,
  },
  analyzing: {
    label: "Analyzing Resume...",
    description: "Building your ATS, career-match, and interview insights.",
    target: 92,
  },
};

export function AnalysisLoadingScreen({ phase }: { phase: AnalysisPhase }) {
  const [progress, setProgress] = useState(phase === "uploading" ? 12 : 52);
  const details = phaseDetails[phase];

  useEffect(() => {
    setProgress(phase === "uploading" ? 12 : 52);
    const timer = window.setInterval(() => {
      setProgress((current) => Math.min(details.target, current + 2));
    }, 260);

    return () => window.clearInterval(timer);
  }, [details.target, phase]);

  return (
    <motion.section
      aria-live="polite"
      className="mx-auto flex min-h-[60vh] max-w-xl items-center"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <Card className="w-full p-8 text-center sm:p-10">
        <motion.div
          className="mx-auto flex size-16 items-center justify-center rounded-2xl bg-teal-500/10 text-teal-600 dark:text-teal-300"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, ease: "linear", repeat: Number.POSITIVE_INFINITY }}
        >
          {phase === "uploading" ? <FileSearch className="size-8" /> : <Sparkles className="size-8" />}
        </motion.div>
        <div className="mt-6 flex items-center justify-center gap-2">
          <LoaderCircle className="size-5 animate-spin text-teal-600 dark:text-teal-300" />
          <h1 className="text-2xl font-bold tracking-tight">{details.label}</h1>
        </div>
        <p className="mt-3 text-sm text-[var(--muted)]">{details.description}</p>
        <div className="mt-8 text-left">
          <div className="mb-2 flex justify-between text-xs font-semibold text-[var(--muted)]">
            <span>Analysis in progress</span>
            <span>{progress}%</span>
          </div>
          <Progress value={progress} />
        </div>
      </Card>
    </motion.section>
  );
}
