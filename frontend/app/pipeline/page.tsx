"use client";

import { useState } from "react";

import { StepResumeAnalyzer } from "@/components/wizard/step-resume-analyzer";
import { Stepper, WizardStepId } from "@/components/wizard/stepper";
import { WizardShell } from "@/components/wizard/wizard-shell";

const STEP_META: Record<WizardStepId, { title: string; description: string }> = {
  resume: {
    title: "Resume Analyzer",
    description: "Upload your resume to get an ATS-readability score before moving through the rest of the pipeline.",
  },
  suggestions: { title: "Improvement Suggestions", description: "Coming soon." },
  jobs: { title: "Live Job Discovery", description: "Coming soon." },
  fit: { title: "Fit Analysis", description: "Coming soon." },
  tailor: { title: "Tailor & Prep", description: "Coming soon." },
  outreach: { title: "Recruiter Outreach", description: "Coming soon." },
};

export default function PipelinePage() {
  const [activeStep, setActiveStep] = useState<WizardStepId>("resume");
  const [completedSteps, setCompletedSteps] = useState<WizardStepId[]>([]);

  const meta = STEP_META[activeStep];

  return (
    <WizardShell
      title={meta.title}
      description={meta.description}
      stepper={<Stepper activeStep={activeStep} completedSteps={completedSteps} onSelect={setActiveStep} />}
    >
      {activeStep === "resume" && (
        <StepResumeAnalyzer
          onComplete={() => {
            setCompletedSteps((prev) => (prev.includes("resume") ? prev : [...prev, "resume"]));
            // Steps 2-6 are not built yet in this phase of the rebuild.
          }}
        />
      )}
    </WizardShell>
  );
}
