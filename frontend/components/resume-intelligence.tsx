"use client";

import { ChangeEvent, useEffect, useState } from "react";

type Analysis = {
  ats_estimate: number;
  score_breakdown: { name: string; score: number; weight: number; explanation: string }[];
  profile: { name: string | null; contact: { email: string | null; phone: string | null }; education: string; experience: string; projects: string; certifications: string; achievements: string; sections_present: string[]; skills: string[] };
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  skill_signals: string[];
  extracted_text: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function ResumeIntelligence({ onNavigate }: { onNavigate?: (tab: "Resume" | "Job Intelligence" | "Interview" | "Applications" | "AI Society") => void }) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [status, setStatus] = useState("Upload a text-based PDF resume to begin.");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    if (!resumeId || analysis) return;
    void fetch(`${apiUrl}/api/resumes/${encodeURIComponent(resumeId)}`)
      .then(async (response) => {
        if (!response.ok) throw new Error("Stored analysis unavailable.");
        return response.json() as Promise<Analysis>;
      })
      .then((stored) => {
        setAnalysis(stored);
        setStatus("Analysis complete. Ready for your next move.");
      })
      .catch(() => setStatus("Upload a text-based PDF resume to begin."));
  }, [analysis]);

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setAnalysis(null);
    setStatus("Uploading and preparing your resume...");
    const form = new FormData();
    form.append("file", file);
    try {
      const uploadResponse = await fetch(`${apiUrl}/api/resumes/upload`, { method: "POST", body: form });
      const uploaded = await uploadResponse.json();
      if (!uploadResponse.ok) throw new Error(uploaded.detail ?? "Upload failed.");
      setStatus("Resume uploaded. Running transparent compatibility analysis...");
      const analysisResponse = await fetch(`${apiUrl}/api/resumes/${uploaded.resume_id}/analyze`, { method: "POST" });
      const result = await analysisResponse.json();
      if (!analysisResponse.ok) throw new Error(result.detail ?? "Analysis failed.");
      setAnalysis(result);
      window.localStorage.setItem("careerpilot_resume_id", uploaded.resume_id);
      setStatus("Analysis complete.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Resume analysis failed.");
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5 md:col-span-2">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm text-indigo-300">Resume Intelligence Agent</p>
          <h2 className="mt-2 text-xl font-medium">Understand your resume</h2>
          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-400">Get grounded strengths, gaps, skill signals, and an explainable compatibility estimate.</p>
        </div>
        <label className="cursor-pointer rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400">
          {busy ? "Processing..." : "Upload PDF"}
          <input className="hidden" type="file" accept="application/pdf,.pdf" onChange={upload} disabled={busy} />
        </label>
      </div>
      <p className="mt-5 text-xs text-slate-500">{status}</p>
      {analysis && <AnalysisView analysis={analysis} onNavigate={onNavigate} />}
    </div>
  );
}

function AnalysisView({ analysis, onNavigate }: { analysis: Analysis; onNavigate?: (tab: "Resume" | "Job Intelligence" | "Interview" | "Applications" | "AI Society") => void }) {
  return (
    <div className="mt-6 space-y-5 border-t border-white/10 pt-5">
      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Compatibility estimate" value={`${analysis.ats_estimate}/100`} />
        <Metric label="Sections detected" value={`${analysis.profile.sections_present.length}/6`} />
        <Metric label="Skill signals" value={`${analysis.skill_signals.length}`} />
      </div>
      {onNavigate && (
        <div className="flex flex-wrap gap-2 pt-1">
          <button
            type="button"
            onClick={() => onNavigate("Job Intelligence")}
            className="rounded-lg bg-indigo-500/20 border border-indigo-400/30 px-3.5 py-1.5 text-xs font-medium text-indigo-200 hover:bg-indigo-500/30 transition-colors"
          >
            Find Matching Jobs in Job Intelligence →
          </button>
        </div>
      )}
      <p className="rounded-lg border border-indigo-400/20 bg-indigo-400/10 p-3 text-xs leading-5 text-indigo-100">
        This is a CareerPilot compatibility estimate, not a prediction of how a specific ATS will score your resume.
      </p>
      <div>
        <h3 className="text-sm font-medium">Score breakdown</h3>
        <div className="mt-3 space-y-3">
          {analysis.score_breakdown.map((item) => (
            <div key={item.name}>
              <div className="flex justify-between text-xs"><span>{item.name}</span><span>{item.score}/100 · {item.weight}% weight</span></div>
              <div className="mt-1 h-1.5 rounded-full bg-white/10"><div className="h-1.5 rounded-full bg-indigo-400" style={{ width: `${item.score}%` }} /></div>
              <p className="mt-1 text-xs text-slate-500">{item.explanation}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <Insight title="Strengths" items={analysis.strengths} empty="No strong signals detected yet." color="text-emerald-300" />
        <Insight title="Weaknesses" items={analysis.weaknesses} empty="No major weaknesses detected." color="text-amber-300" />
      </div>
      <Insight title="Recommendations" items={analysis.recommendations} empty="No recommendations yet." color="text-indigo-300" />
      <div>
        <h3 className="text-sm font-medium">Extracted profile</h3>
        <div className="mt-3 grid gap-3 text-sm text-slate-300 sm:grid-cols-2">
          <p><span className="text-slate-500">Name:</span> {analysis.profile.name ?? "Not detected"}</p>
          <p><span className="text-slate-500">Email:</span> {analysis.profile.contact.email ?? "Not detected"}</p>
          <p><span className="text-slate-500">Phone:</span> {analysis.profile.contact.phone ?? "Not detected"}</p>
          <p><span className="text-slate-500">Skills:</span> {analysis.skill_signals.join(", ") || "None detected"}</p>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-white/10 bg-slate-950/30 p-3"><p className="text-xs text-slate-500">{label}</p><p className="mt-1 text-lg font-semibold">{value}</p></div>;
}

function Insight({ title, items, empty, color }: { title: string; items: string[]; empty: string; color: string }) {
  return <div><h3 className={`text-sm font-medium ${color}`}>{title}</h3><ul className="mt-2 space-y-2 text-sm leading-5 text-slate-300">{(items.length ? items : [empty]).map((item) => <li className="rounded-lg bg-white/[0.03] p-3" key={item}>{item}</li>)}</ul></div>;
}
