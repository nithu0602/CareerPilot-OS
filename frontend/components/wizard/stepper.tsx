"use client";

import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

export type WizardStepId =
  | "resume"
  | "suggestions"
  | "jobs"
  | "fit"
  | "tailor"
  | "outreach";

export interface WizardStepDef {
  id: WizardStepId;
  label: string;
  available: boolean;
}

export const WIZARD_STEPS: WizardStepDef[] = [
  { id: "resume", label: "Resume Analyzer", available: true },
  { id: "suggestions", label: "Suggestions", available: false },
  { id: "jobs", label: "Job Discovery", available: false },
  { id: "fit", label: "Fit Analysis", available: false },
  { id: "tailor", label: "Tailor & Prep", available: false },
  { id: "outreach", label: "Recruiter Outreach", available: false },
];

export function Stepper({
  activeStep,
  completedSteps,
  onSelect,
}: {
  activeStep: WizardStepId;
  completedSteps: WizardStepId[];
  onSelect: (step: WizardStepId) => void;
}) {
  return (
    <ol
      aria-label="CareerPilot pipeline progress"
      className="flex flex-wrap items-center gap-x-1 gap-y-3 overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3"
    >
      {WIZARD_STEPS.map((step, index) => {
        const isActive = step.id === activeStep;
        const isDone = completedSteps.includes(step.id);
        const canSelect = step.available && (isDone || isActive);
        return (
          <li key={step.id} className="flex items-center">
            <button
              type="button"
              disabled={!canSelect}
              aria-current={isActive ? "step" : undefined}
              onClick={() => canSelect && onSelect(step.id)}
              className={cn(
                "flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                isActive && "bg-[var(--primary)]/15 text-[var(--accent)]",
                !isActive && isDone && "text-[var(--success)] hover:bg-white/5",
                !isActive && !isDone && step.available && "text-[var(--muted)] hover:bg-white/5",
                !step.available && "cursor-not-allowed text-[var(--muted)]/40",
              )}
            >
              <span
                className={cn(
                  "flex h-5 w-5 items-center justify-center rounded-full border text-[10px]",
                  isActive && "border-[var(--accent)] text-[var(--accent)]",
                  !isActive && isDone && "border-[var(--success)] bg-[var(--success)]/20 text-[var(--success)]",
                  !isActive && !isDone && "border-[var(--border)]",
                )}
                aria-hidden="true"
              >
                {isDone ? <Check size={12} /> : index + 1}
              </span>
              {step.label}
              {!step.available && <span className="sr-only"> (coming soon)</span>}
            </button>
            {index < WIZARD_STEPS.length - 1 && (
              <span className="mx-1 hidden h-px w-4 bg-[var(--border)] sm:block" aria-hidden="true" />
            )}
          </li>
        );
      })}
    </ol>
  );
}
