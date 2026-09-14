"use client";

import { useEffect, useState } from "react";

type Question = { question: string; label: string; relevant_evidence: string; key_points: string[]; missing_evidence_caution: string };
type Preparation = { resume_recommendations: string[]; sections_to_emphasize: string[]; skills_to_highlight: string[]; likely_questions: Question[]; talking_points: { subject: string; why_relevant: string; skills_demonstrated: string[]; talking_points: string[]; evidence_source: string }[]; evidence_note: string };
type Application = { application_id: string; job_id: string; job_title: string; company: string; application_url: string | null; state: string; fit_score: number | null; sponsorship_status: string | null; salary: string | null; deadline: string | null; preparation: Preparation | null };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const states = ["SAVED", "PREPARING", "READY_TO_APPLY", "APPLIED", "INTERVIEW", "OFFER", "REJECTED"];

export function Applications({ onNavigate }: { onNavigate?: (tab: "Resume" | "Job Intelligence" | "Interview" | "Applications" | "AI Society") => void }) {
  const [applications, setApplications] = useState<Application[]>([]);
  const [selected, setSelected] = useState<Application | null>(null);
  const [message, setMessage] = useState("Loading applications...");
  async function load() {
    const response = await fetch(`${apiUrl}/api/applications`);
    if (!response.ok) { setMessage("Could not load applications."); return; }
    const data: Application[] = await response.json(); setApplications(data); setSelected((current) => current ? data.find((item) => item.application_id === current.application_id) ?? current : data[0] ?? null); setMessage("");
  }
  useEffect(() => { void load(); }, []);
  async function create() {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    const jobId = window.localStorage.getItem("careerpilot_job_id");
    if (!resumeId || !jobId) { setMessage("Analyze a resume and select a job first."); return; }
    const response = await fetch(`${apiUrl}/api/applications`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume_id: resumeId, job_id: jobId }) });
    const data = await response.json(); if (!response.ok) { setMessage(data.detail ?? "Could not create application."); return; } await load(); setSelected(data);
  }
  async function prepare() {
    if (!selected) return;
    const response = await fetch(`${apiUrl}/api/applications/${selected.application_id}/prepare`, { method: "POST" });
    const data = await response.json(); if (!response.ok) { setMessage(data.detail ?? "Could not prepare application."); return; } setSelected(data); await load();
  }
  async function updateState(state: string) {
    if (!selected) return;
    const response = await fetch(`${apiUrl}/api/applications/${selected.application_id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ state }) });
    if (response.ok) { setSelected(await response.json()); await load(); }
  }
  return <section className="rounded-xl border border-white/10 bg-white/[0.03] p-5 md:col-span-3"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm text-indigo-300">Applications</p><h2 className="mt-2 text-xl font-medium">Prepare, then apply manually</h2><p className="mt-2 text-sm text-slate-400">CareerPilot never submits external applications.</p></div><button onClick={create} className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium">Create from selected job</button></div>{message && <p className="mt-4 text-xs text-slate-500">{message}</p>}<div className="mt-5 grid gap-4 lg:grid-cols-[1fr_1.4fr]"><div className="space-y-2">{applications.map((item) => <button key={item.application_id} onClick={() => setSelected(item)} className={`w-full rounded-lg border p-3 text-left ${selected?.application_id === item.application_id ? "border-indigo-400/50 bg-indigo-400/10" : "border-white/10"}`}><p className="text-sm font-medium">{item.job_title}</p><p className="mt-1 text-xs text-slate-400">{item.company} · {item.state}</p></button>)}</div>{selected ? <Detail application={selected} onPrepare={prepare} onUpdate={updateState} onNavigate={onNavigate} /> : <p className="rounded-lg border border-dashed border-white/10 p-5 text-sm text-slate-500">Create an application from a selected job.</p>}</div></section>;
}

function Detail({ application, onPrepare, onUpdate, onNavigate }: { application: Application; onPrepare: () => void; onUpdate: (state: string) => void; onNavigate?: (tab: "Resume" | "Job Intelligence" | "Interview" | "Applications" | "AI Society") => void }) {
  const preparation = application.preparation;
  return <article className="rounded-lg border border-white/10 bg-slate-950/25 p-5"><div className="flex flex-wrap justify-between gap-3"><div><h3 className="text-lg font-medium">{application.job_title}</h3><p className="mt-1 text-sm text-slate-400">{application.company} · Fit {application.fit_score === null ? "not analyzed" : `${application.fit_score}/100`}</p></div><span className="rounded-full bg-indigo-400/15 px-3 py-1 text-xs text-indigo-200">{application.state}</span></div><div className="mt-4 grid gap-2 text-sm sm:grid-cols-3"><p><span className="text-slate-500">Salary:</span> {application.salary ?? "Not disclosed"}</p><p><span className="text-slate-500">Deadline:</span> {application.deadline ?? "Not disclosed"}</p><p><span className="text-slate-500">Sponsorship:</span> {application.sponsorship_status ?? "Not analyzed"}</p></div><div className="mt-4 flex flex-wrap gap-2"><button onClick={onPrepare} className="rounded-lg bg-indigo-500 px-3 py-2 text-xs font-medium">Prepare</button>{application.application_url && <a href={application.application_url} target="_blank" rel="noreferrer" className="rounded-lg bg-white/10 px-3 py-2 text-xs">Open application</a>}<select value={application.state} onChange={(event) => onUpdate(event.target.value)} className="rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-xs"><option disabled>Update status</option>{states.map((state) => <option key={state}>{state}</option>)}</select></div>{preparation ? <div className="mt-5 space-y-5 border-t border-white/10 pt-5"><p className="text-xs text-slate-400">{preparation.evidence_note}</p><Block title="Tailored resume recommendations" items={preparation.resume_recommendations} /><Block title="Sections to emphasize" items={preparation.sections_to_emphasize} /><Block title="Skills to highlight" items={preparation.skills_to_highlight} /><div><h4 className="text-sm font-medium">Likely application questions</h4>{preparation.likely_questions.map((question) => <div key={question.question} className="mt-3 rounded-lg border border-white/10 p-3 text-sm"><p className="text-indigo-200">{question.label}: {question.question}</p><p className="mt-2 text-xs text-slate-300">Relevant evidence: {question.relevant_evidence}</p><Block title="Key points" items={question.key_points} /><p className="mt-2 text-xs text-amber-200">Caution: {question.missing_evidence_caution}</p></div>)}</div><div><h4 className="text-sm font-medium">Project / experience talking points</h4>{preparation.talking_points.map((point) => <div key={point.subject} className="mt-3 rounded-lg border border-white/10 p-3 text-sm"><p className="font-medium">{point.subject}</p><p className="mt-1 text-xs text-slate-400">{point.why_relevant}</p><Block title="Talking points" items={point.talking_points} /><p className="text-xs text-slate-500">Evidence: {point.evidence_source}</p></div>)}</div></div> : <p className="mt-5 text-sm text-slate-500">Prepare this application to generate grounded materials.</p>}</article>;
}
function Block({ title, items }: { title: string; items: string[] }) { return <div className="mt-3"><h5 className="text-xs text-slate-500">{title}</h5>{items.length ? <ul className="mt-1 list-disc pl-5 text-sm text-slate-300">{items.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="mt-1 text-xs text-slate-500">No supported evidence available.</p>}</div>; }
