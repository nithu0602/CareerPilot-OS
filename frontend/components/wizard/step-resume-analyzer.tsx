"use client";

import { AlertTriangle, CheckCircle2, Loader2, Upload } from "lucide-react";
import { ChangeEvent, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress, ScoreRing } from "@/components/ui/progress";

type Analysis = {
  resume_id: string;
  ats_estimate: number;
  score_breakdown: { name: string; score: number; weight: number; explanation: string }[];
  profile: {
    name: string | null;
    contact: { email: string | null; phone: string | null };
    skills: string[];
    sections_present: string[];
  };
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
};

type LoadState = "idle" | "uploading" | "analyzing" | "done" | "error";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function StepResumeAnalyzer({ onComplete }: { onComplete: (resumeId: string) => void }) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [state, setState] = useState<LoadState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setAnalysis(null);
    setError(null);
    setState("uploading");
    const form = new FormData();
    form.append("file", file);
    try {
      const uploadResponse = await fetch(`${apiUrl}/api/resumes/upload`, { method: "POST", body: form });
      const uploaded = await uploadResponse.json();
      if (!uploadResponse.ok) throw new Error(uploaded.detail ?? "Upload failed.");

      setState("analyzing");
      const analysisResponse = await fetch(`${apiUrl}/api/resumes/${uploaded.resume_id}/analyze`, { method: "POST" });
      const result = await analysisResponse.json();
      if (!analysisResponse.ok) throw new Error(result.detail ?? "Analysis failed.");

      setAnalysis(result);
      setPreviewUrl(`${apiUrl}/api/resumes/${uploaded.resume_id}/file`);
      window.localStorage.setItem("careerpilot_resume_id", uploaded.resume_id);
      setState("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Resume analysis failed. Please try again.");
      setState("error");
    } finally {
      event.target.value = "";
    }
  }

  const busy = state === "uploading" || state === "analyzing";

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Resume Analyzer</CardTitle>
            <CardDescription>
              Upload a text-based PDF resume to get an ATS-readability score and a breakdown of what to fix first.
            </CardDescription>
          </div>
          <label>
            <Button asChild variant="primary" size="md">
              <span className="cursor-pointer">
                {busy ? <Loader2 className="animate-spin" size={16} /> : <Upload size={16} />}
                {busy ? "Processing..." : "Upload PDF"}
              </span>
            </Button>
            <input className="hidden" type="file" accept="application/pdf,.pdf" onChange={upload} disabled={busy} />
          </label>
        </CardHeader>

        {state === "idle" && (
          <p className="rounded-lg border border-dashed border-[var(--border)] p-6 text-center text-sm text-[var(--muted)]">
            No resume uploaded yet. Choose a PDF above to begin.
          </p>
        )}

        {busy && (
          <div className="flex items-center gap-3 rounded-lg border border-[var(--border)] bg-white/[0.02] p-4 text-sm text-[var(--muted)]">
            <Loader2 className="animate-spin text-[var(--accent)]" size={18} />
            {state === "uploading" ? "Uploading your resume..." : "Scoring readability, keywords, and structure..."}
          </div>
        )}

        {state === "error" && error && (
          <div
            role="alert"
            className="flex items-start gap-3 rounded-lg border border-[var(--error)]/30 bg-[var(--error)]/10 p-4 text-sm text-[var(--error)]"
          >
            <AlertTriangle size={18} className="mt-0.5 shrink-0" />
            <div>
              <p className="font-medium">We couldn&apos;t analyze this resume.</p>
              <p className="mt-1 text-[var(--foreground)]/80">{error}</p>
            </div>
          </div>
        )}

        {analysis && previewUrl && (
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2">
              <div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-[var(--border)] bg-white/[0.02] p-6">
                <ScoreRing value={analysis.ats_estimate} label="ATS readability score" />
                <p className="max-w-xs text-center text-xs text-[var(--muted)]">
                  A CareerPilot compatibility estimate based on formatting, keywords, and structure — not a guarantee of
                  how any specific employer&apos;s ATS will score this resume.
                </p>
              </div>
              <div className="overflow-hidden rounded-lg border border-[var(--border)]">
                <iframe title="Resume preview" src={previewUrl} className="h-64 w-full md:h-full" />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium">Score breakdown</h3>
              <div className="mt-3 space-y-3">
                {analysis.score_breakdown.map((item) => (
                  <div key={item.name}>
                    <div className="flex justify-between text-xs text-[var(--muted)]">
                      <span className="text-[var(--foreground)]">{item.name}</span>
                      <span>
                        {item.score}/100 · {item.weight}% weight
                      </span>
                    </div>
                    <Progress value={item.score} className="mt-1.5" />
                    <p className="mt-1 text-xs text-[var(--muted)]">{item.explanation}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <InsightList title="Strengths" items={analysis.strengths} tone="success" empty="No strong signals detected yet." />
              <InsightList title="Weaknesses" items={analysis.weaknesses} tone="warning" empty="No major weaknesses detected." />
            </div>
            <InsightList title="Recommendations" items={analysis.recommendations} tone="primary" empty="No recommendations yet." />

            <div className="flex items-center justify-between rounded-lg border border-[var(--success)]/30 bg-[var(--success)]/10 p-4">
              <div className="flex items-center gap-2 text-sm text-[var(--success)]">
                <CheckCircle2 size={18} />
                Scoring complete — ready to continue.
              </div>
              <Button variant="primary" onClick={() => onComplete(analysis.resume_id)}>
                Next: Suggestions
              </Button>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  );
}

function InsightList({
  title,
  items,
  empty,
  tone,
}: {
  title: string;
  items: string[];
  empty: string;
  tone: "success" | "warning" | "primary";
}) {
  return (
    <div>
      <h3 className="mb-2 text-sm font-medium">
        <Badge tone={tone}>{title}</Badge>
      </h3>
      <ul className="space-y-2 text-sm leading-5 text-[var(--foreground)]/90">
        {(items.length ? items : [empty]).map((item) => (
          <li className="rounded-lg bg-white/[0.03] p-3" key={item}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
