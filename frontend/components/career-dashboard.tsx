"use client";

import { useEffect, useState } from "react";

type Action = { action_id: string; action: string; priority: string; title: string; reason: string; supporting_evidence: string[]; suggested_next_step: string; related_job_id?: string | null; related_skill?: string | null };
type Dashboard = { resume_score: number | null; job_count: number; high_fit_jobs: { job_id: string; fit_score: number }[]; active_interviews: number; completed_interviews: number; top_skill_gaps: { skill: string; frequency: number }[]; next_best_action: Action | null; actions: Action[]; notes: string[] };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function CareerDashboard() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [message, setMessage] = useState("Loading career overview...");

  async function load() {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    const query = resumeId ? `?resume_id=${encodeURIComponent(resumeId)}` : "";
    const response = await fetch(`${apiUrl}/api/career/dashboard${query}`);
    if (!response.ok) { setMessage("Career overview is temporarily unavailable."); return; }
    setData(await response.json());
    setMessage("");
  }

  useEffect(() => { void load(); }, []);

  return <section className="rounded-xl border border-indigo-400/30 bg-indigo-400/[0.08] p-5 md:col-span-3"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm text-indigo-200">Career Strategist</p><h2 className="mt-2 text-2xl font-semibold">Your next career move</h2><p className="mt-2 text-sm text-slate-300">Evidence from your resume, jobs, fit analyses, and interviews — not an automatic application.</p></div><button onClick={() => void load()} className="rounded-lg bg-white/10 px-3 py-2 text-xs text-slate-200">Refresh</button></div>{message && <p className="mt-4 text-xs text-slate-400">{message}</p>}{data && <div className="mt-5 space-y-5"><div className="grid gap-3 sm:grid-cols-4"><Metric label="Resume estimate" value={data.resume_score === null ? "Not ready" : `${data.resume_score}/100`} /><Metric label="Jobs available" value={`${data.job_count}`} /><Metric label="High-fit jobs" value={`${data.high_fit_jobs.length}`} /><Metric label="Interviews" value={`${data.active_interviews + data.completed_interviews}`} /></div>{data.next_best_action ? <ActionCard action={data.next_best_action} prominent /> : <p className="rounded-lg border border-white/10 p-4 text-sm text-slate-300">No next action yet. Analyze a resume and at least one job to build an evidence-based plan.</p>}<div className="grid gap-4 md:grid-cols-2"><div><h3 className="text-sm font-medium">Priority skill gaps</h3><div className="mt-3 space-y-2">{data.top_skill_gaps.length ? data.top_skill_gaps.map((gap) => <p key={gap.skill} className="rounded-lg bg-slate-950/30 p-3 text-sm">{gap.skill}<span className="float-right text-xs text-slate-400">{gap.frequency} job{gap.frequency === 1 ? "" : "s"}</span></p>) : <p className="mt-2 text-sm text-slate-400">No skill gaps available yet.</p>}</div></div><div><h3 className="text-sm font-medium">Next actions</h3><div className="mt-3 space-y-2">{data.actions.slice(0, 4).map((action) => <ActionCard key={action.action_id} action={action} />)}</div></div></div>{data.notes.map((note) => <p key={note} className="text-xs text-slate-500">{note}</p>)}</div>}</section>;
}

function ActionCard({ action, prominent = false }: { action: Action; prominent?: boolean }) {
  return <article className={`rounded-lg border p-4 ${prominent ? "border-indigo-300/40 bg-indigo-950/30" : "border-white/10 bg-slate-950/20"}`}><div className="flex items-start justify-between gap-3"><div><p className="text-[10px] uppercase tracking-wide text-indigo-300">{action.priority} · {action.action}</p><h3 className={prominent ? "mt-2 text-lg font-medium" : "mt-1 text-sm font-medium"}>{prominent ? "NEXT BEST ACTION: " : ""}{action.title}</h3></div></div><p className="mt-2 text-sm text-slate-300">{action.reason}</p><ul className="mt-2 space-y-1 text-xs text-slate-400">{action.supporting_evidence.map((item) => <li key={item}>• {item}</li>)}</ul><p className="mt-3 text-xs text-indigo-200">Suggested next step: {action.suggested_next_step}</p></article>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-white/10 bg-slate-950/25 p-3"><p className="text-xs text-slate-500">{label}</p><p className="mt-1 text-lg font-semibold">{value}</p></div>;
}
