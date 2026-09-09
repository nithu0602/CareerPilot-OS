"use client";

import { FormEvent, useEffect, useState } from "react";

type Job = {
  job_id: string; title: string; company: string; location: string | null; employment_type: string | null;
  salary: string | null; deadline: string | null; source_url: string | null; description: string | null;
  requirements: string[]; responsibilities: string[]; required_skills: string[]; preferred_skills: string[];
  eligibility: string | null; sponsorship_information: string | null; mode: "demo" | "live";
  category: string | null; experience_level: string | null; work_mode: string | null; source_domain: string | null;
  provenance: { source_name: string; salary_source: string | null; deadline_source: string | null; requirements_source: string | null };
};
type Match = {
  fit_score: number;
  score_breakdown: { name: string; score: number; weight: number; explanation: string }[];
  skill_gaps: { skill: string; category: string; why_it_matters: string; candidate_evidence: string; recommended_action: string }[];
  sponsorship: { classification: string; evidence_quote: string | null; source_url: string | null; reasoning: string; fact: string; inference: string };
  salary: string | null; salary_evidence: string | null; deadline: string | null; deadline_evidence: string | null;
  why_this_match: string[]; why_not_100: string[]; recommended_next_step: string;
};
type SearchResponse = { jobs: Job[]; mode: "demo" | "live" | "fallback"; fallback_reason?: string | null; total: number; queries_used: string[]; result_note?: string | null };
type Option = { value: string; label: string };
type SearchOptions = { categories: Option[]; locations: string[]; default_location: string; experience_levels: Option[]; default_experience: string; work_modes: Option[]; default_work_mode: string };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function JobIntelligence() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selected, setSelected] = useState<Job | null>(null);
  const [mode, setMode] = useState<"demo" | "live">("demo");
  const [options, setOptions] = useState<SearchOptions | null>(null);
  const [category, setCategory] = useState("DATA");
  const [location, setLocation] = useState("London");
  const [experience, setExperience] = useState("GRADUATE");
  const [workMode, setWorkMode] = useState("ANY");
  const [keyword, setKeyword] = useState("");
  const [message, setMessage] = useState("Loading cached demo jobs...");
  const [match, setMatch] = useState<Match | null>(null);
  const [matchMessage, setMatchMessage] = useState("");

  async function loadOptions() {
    const response = await fetch(`${apiUrl}/api/jobs/options`);
    if (!response.ok) return;
    const data: SearchOptions = await response.json();
    setOptions(data);
    setLocation(data.default_location);
    setExperience(data.default_experience);
    setWorkMode(data.default_work_mode);
  }

  async function search(event?: FormEvent) {
    event?.preventDefault();
    setMessage("Searching job sources...");
    const response = await fetch(`${apiUrl}/api/jobs/search`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location, keyword, mode, category, experience, work_mode: workMode }),
    });
    const result: SearchResponse = await response.json();
    if (!response.ok) { setMessage("Job search failed."); return; }
    setJobs(result.jobs);
    setSelected(result.jobs[0] ?? null);
    setMatch(null);
    if (result.fallback_reason) setMessage(`Fallback to cached demo jobs: ${result.fallback_reason}`);
    else setMessage(result.result_note ?? `${result.total} jobs loaded in ${result.mode} mode.`);
  }

  useEffect(() => { void loadOptions().then(() => search()); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const domains = new Set(jobs.map((job) => job.source_domain).filter(Boolean));

  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.03] p-5 md:col-span-3">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><p className="text-sm text-indigo-300">Job Intelligence</p><h2 className="mt-2 text-xl font-medium">Find opportunities</h2><p className="mt-2 text-sm text-slate-400">UK graduate, internship, and entry-level roles. Search cached demo jobs or the live Anakin connector.</p></div>
        <div className="flex rounded-lg border border-white/10 p-1 text-xs">
          {(["demo", "live"] as const).map((value) => <button key={value} onClick={() => setMode(value)} className={`rounded-md px-3 py-1.5 capitalize ${mode === value ? "bg-indigo-500 text-white" : "text-slate-400"}`}>{value}</button>)}
        </div>
      </div>
      <form className="mt-5 space-y-2" onSubmit={search}>
        <div className="grid gap-2 sm:grid-cols-4">
          <select value={category} onChange={(event) => setCategory(event.target.value)} className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm outline-none">
            {(options?.categories ?? []).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
          <select value={location} onChange={(event) => setLocation(event.target.value)} className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm outline-none">
            {(options?.locations ?? ["London"]).map((value) => <option key={value} value={value}>{value}</option>)}
          </select>
          <select value={experience} onChange={(event) => setExperience(event.target.value)} className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm outline-none">
            {(options?.experience_levels ?? []).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
          <select value={workMode} onChange={(event) => setWorkMode(event.target.value)} className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm outline-none">
            {(options?.work_modes ?? []).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </div>
        <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
          <input className="rounded-lg border border-white/10 bg-slate-950/40 px-3 py-2 text-sm outline-none" placeholder="Keyword (optional)" value={keyword} onChange={(event) => setKeyword(event.target.value)} />
          <button className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white" type="submit">Search</button>
        </div>
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-400">
          <span>Popular:</span>
          {(options?.categories ?? []).map((option) => (
            <button type="button" key={option.value} onClick={() => { setCategory(option.value); void search(); }} className={`rounded-full border px-2.5 py-1 ${category === option.value ? "border-indigo-400/60 bg-indigo-400/10 text-indigo-200" : "border-white/10 text-slate-400"}`}>{option.label}</button>
          ))}
        </div>
      </form>
      <p className="mt-3 text-xs text-slate-500">{message}</p>
      {jobs.length > 0 && <p className="mt-1 text-[11px] text-slate-600">{jobs.length} result{jobs.length === 1 ? "" : "s"} · {domains.size || 1} source{domains.size === 1 ? "" : "s"}</p>}
      <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_1.2fr]">
        <div className="space-y-2">
          {jobs.map((job) => <JobCard key={job.job_id} job={job} selected={selected?.job_id === job.job_id} onSelect={() => { setSelected(job); setMatch(null); window.localStorage.setItem("careerpilot_job_id", job.job_id); }} />)}
        </div>
        {selected ? <JobDetail job={selected} match={match} matchMessage={matchMessage} onAnalyze={async () => {
          const resumeId = window.localStorage.getItem("careerpilot_resume_id");
          if (!resumeId) { setMatchMessage("Analyze a resume first to calculate this match."); return; }
          setMatchMessage("Calculating transparent fit intelligence...");
          const response = await fetch(`${apiUrl}/api/jobs/${selected.job_id}/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume_id: resumeId }) });
          const result = await response.json();
          if (!response.ok) { setMatchMessage(result.detail ?? "Match analysis failed."); return; }
          setMatch(result); setMatchMessage("Match analysis complete.");
        }} /> : <div className="rounded-lg border border-dashed border-white/10 p-6 text-sm text-slate-500">Select a job to inspect its source details.</div>}
      </div>
    </section>
  );
}

function JobCard({ job, selected, onSelect }: { job: Job; selected: boolean; onSelect: () => void }) {
  return (
    <button onClick={onSelect} className={`w-full rounded-lg border p-3 text-left ${selected ? "border-indigo-400/60 bg-indigo-400/10" : "border-white/10 bg-white/[0.02]"}`}>
      <div className="flex justify-between gap-2"><span className="text-sm font-medium">{job.title}</span><span className="text-[10px] uppercase text-slate-500">{job.mode}</span></div>
      <p className="mt-1 text-xs text-slate-400">{job.company} · {job.location ?? "Location unavailable"}</p>
      <p className="mt-1 flex flex-wrap gap-x-2 text-[11px] text-slate-500">
        {job.work_mode && <span>{job.work_mode.replace("_", "-").toLowerCase()}</span>}
        {job.experience_level && <span>· {job.experience_level.replace("_", " ").toLowerCase()}</span>}
        {job.salary && <span>· {job.salary}</span>}
      </p>
    </button>
  );
}

function JobDetail({ job, match, matchMessage, onAnalyze }: { job: Job; match: Match | null; matchMessage: string; onAnalyze: () => void }) {
  return <article className="rounded-lg border border-white/10 bg-slate-950/30 p-5"><div className="flex flex-wrap justify-between gap-3"><div><h3 className="text-lg font-medium">{job.title}</h3><p className="mt-1 text-sm text-slate-400">{job.company} · {job.location ?? "Location unavailable"} · {job.employment_type ?? "Type unavailable"}</p></div><span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">{job.mode === "live" ? "Live source" : "Cached demo"}</span></div><div className="mt-5 grid gap-3 text-sm sm:grid-cols-2"><p><span className="text-slate-500">Salary:</span> {job.salary ?? "Not disclosed"}</p><p><span className="text-slate-500">Deadline:</span> {job.deadline ?? "Not disclosed"}</p><p><span className="text-slate-500">Experience:</span> {job.experience_level?.replace("_", " ") ?? "Not disclosed"}</p><p><span className="text-slate-500">Work mode:</span> {job.work_mode?.replace("_", "-") ?? "Not disclosed"}</p></div><DetailList title="Description" items={job.description ? [job.description] : []} /><DetailList title="Requirements" items={job.requirements} /><DetailList title="Responsibilities" items={job.responsibilities} /><DetailList title="Skills" items={[...job.required_skills, ...job.preferred_skills]} /><div className="mt-5 border-t border-white/10 pt-4 text-xs text-slate-500"><p>Source: {job.provenance.source_name}</p><p>Salary evidence: {job.provenance.salary_source ?? "Not available"}</p><p>Deadline evidence: {job.provenance.deadline_source ?? "Not available"}</p>{job.source_url && <a className="mt-2 inline-block text-indigo-300 hover:underline" href={job.source_url} target="_blank" rel="noreferrer">View source ↗</a>}</div><button onClick={onAnalyze} className="mt-5 rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white">Analyze fit</button>{matchMessage && <p className="mt-2 text-xs text-slate-400">{matchMessage}</p>}{match && <MatchView match={match} />}</article>;
}

function MatchView({ match }: { match: Match }) {
  return <div className="mt-6 space-y-5 border-t border-white/10 pt-5"><div className="flex items-center justify-between"><h4 className="text-base font-medium">CareerPilot Fit</h4><span className="text-2xl font-semibold text-indigo-300">{match.fit_score}/100</span></div><div><h4 className="text-sm font-medium">Why this match</h4><DetailList title="" items={match.why_this_match} /></div><div><h4 className="text-sm font-medium">Score breakdown</h4><div className="mt-2 space-y-2">{match.score_breakdown.map((item) => <div key={item.name}><div className="flex justify-between text-xs"><span>{item.name}</span><span>{item.score}/100 · {item.weight}%</span></div><div className="mt-1 h-1 rounded-full bg-white/10"><div className="h-1 rounded-full bg-indigo-400" style={{ width: `${item.score}%` }} /></div><p className="mt-1 text-xs text-slate-500">{item.explanation}</p></div>)}</div></div><DetailList title="Why not 100%?" items={match.why_not_100} /><DetailList title="Relevant skill gaps" items={match.skill_gaps.map((gap) => `${gap.skill} — ${gap.category}. ${gap.recommended_action}`)} /><div className="rounded-lg border border-amber-400/20 bg-amber-400/10 p-3 text-sm"><p className="font-medium">Sponsorship: {match.sponsorship.classification}</p><p className="mt-1 text-xs text-slate-300">FACT: {match.sponsorship.fact}</p><p className="mt-1 text-xs text-slate-300">INFERENCE: {match.sponsorship.inference}</p>{match.sponsorship.evidence_quote && <p className="mt-1 text-xs text-slate-300">Evidence: “{match.sponsorship.evidence_quote}”</p>}</div><p className="text-sm"><span className="text-slate-500">Recommended next step:</span> {match.recommended_next_step}</p></div>;
}

function DetailList({ title, items }: { title: string; items: string[] }) {
  return <div className="mt-5">{title && <h4 className="text-sm font-medium">{title}</h4>}{items.length ? <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-5 text-slate-300">{items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}</ul> : <p className="mt-2 text-sm text-slate-500">Not provided.</p>}</div>;
}
