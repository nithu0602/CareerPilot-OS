"use client";

import { useEffect, useState } from "react";

type Action = { action_id: string; action: string; priority: string; title: string; reason: string; suggested_next_step: string };
type Dashboard = { resume_score: number | null; job_count: number; high_fit_jobs: { job_id: string; fit_score: number }[]; active_interviews: number; completed_interviews: number; next_best_action: Action | null };
type Application = { application_id: string; job_title: string; company: string; state: string };
type Job = { job_id: string; title: string; company: string };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Tab = "Overview" | "Resume" | "Job intelligence" | "Interview" | "Applications" | "AI Society";

export function OverviewSummary({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [topJob, setTopJob] = useState<Job | null>(null);
  const [application, setApplication] = useState<Application | null>(null);
  const [message, setMessage] = useState("Loading your career summary...");

  useEffect(() => {
    void (async () => {
      const resumeId = window.localStorage.getItem("careerpilot_resume_id");
      const query = resumeId ? `?resume_id=${encodeURIComponent(resumeId)}` : "";
      const dashboardResponse = await fetch(`${apiUrl}/api/career/dashboard${query}`);
      if (dashboardResponse.ok) {
        const data: Dashboard = await dashboardResponse.json();
        setDashboard(data);
        if (data.high_fit_jobs[0]) {
          const jobResponse = await fetch(`${apiUrl}/api/jobs/${encodeURIComponent(data.high_fit_jobs[0].job_id)}`);
          if (jobResponse.ok) setTopJob(await jobResponse.json());
        }
      }
      const appsResponse = await fetch(`${apiUrl}/api/applications`);
      if (appsResponse.ok) {
        const apps: Application[] = await appsResponse.json();
        setApplication(apps[0] ?? null);
      }
      setMessage("");
    })();
  }, []);

  return (
    <>
      <section className="rounded-xl border border-white/10 bg-white/[0.03] p-5 md:col-span-2">
        <p className="text-sm text-indigo-300">Command center</p>
        <h2 className="mt-2 text-xl font-medium">Your career at a glance</h2>
        {message && <p className="mt-4 text-xs text-slate-500">{message}</p>}
        {dashboard && (
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <SummaryCard
              label="Resume health"
              value={dashboard.resume_score === null ? "Not analyzed" : `${dashboard.resume_score}/100`}
              action="Resume"
              onNavigate={onNavigate}
            />
            <SummaryCard
              label="Top job match"
              value={topJob ? `${topJob.title} — ${dashboard.high_fit_jobs[0].fit_score}/100` : `${dashboard.job_count} jobs available`}
              action="Job intelligence"
              onNavigate={onNavigate}
            />
            <SummaryCard
              label="Interview"
              value={dashboard.active_interviews > 0 ? "In progress" : dashboard.completed_interviews > 0 ? `${dashboard.completed_interviews} completed` : "Not started"}
              action="Interview"
              onNavigate={onNavigate}
            />
            <SummaryCard
              label="Application status"
              value={application ? `${application.job_title} · ${application.state}` : "No application yet"}
              action="Applications"
              onNavigate={onNavigate}
            />
          </div>
        )}
        {dashboard?.next_best_action && (
          <div className="mt-5 rounded-lg border border-indigo-300/40 bg-indigo-950/30 p-4">
            <p className="text-[10px] uppercase tracking-wide text-indigo-300">{dashboard.next_best_action.priority} priority</p>
            <h3 className="mt-1 text-base font-medium">Next best action: {dashboard.next_best_action.title}</h3>
            <p className="mt-2 text-sm text-slate-300">{dashboard.next_best_action.reason}</p>
            <p className="mt-2 text-xs text-indigo-200">{dashboard.next_best_action.suggested_next_step}</p>
          </div>
        )}
      </section>
      <SocietySummary onNavigate={onNavigate} />
    </>
  );
}

function SummaryCard({ label, value, action, onNavigate }: { label: string; value: string; action: Tab; onNavigate: (tab: Tab) => void }) {
  return (
    <button onClick={() => onNavigate(action)} className="rounded-lg border border-white/10 bg-slate-950/25 p-3 text-left hover:border-indigo-400/40">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-medium">{value}</p>
    </button>
  );
}

// A small AI Society summary card. Reuses localStorage state only; does not
// automatically call the Society API (that remains an explicit user action
// on its own dedicated tab, per the existing Society design).
function SocietySummary({ onNavigate }: { onNavigate: (tab: Tab) => void }) {
  const [hasResume, setHasResume] = useState(false);

  useEffect(() => {
    setHasResume(Boolean(window.localStorage.getItem("careerpilot_resume_id")));
  }, []);

  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.03] p-5">
      <p className="text-sm text-indigo-300">AI Society</p>
      <h2 className="mt-2 text-lg font-medium">Collaborative review</h2>
      <p className="mt-2 text-xs text-slate-400">
        {hasResume
          ? "Four specialized agents can review your evidence and propose a next move."
          : "Analyze a resume to unlock the AI Society review."}
      </p>
      <button onClick={() => onNavigate("AI Society")} className="mt-4 w-full rounded-lg bg-white/10 px-3 py-2 text-xs text-slate-200">
        Run AI Society
      </button>
    </section>
  );
}
