"use client";

import { useEffect, useState } from "react";

type AgentStatus = "SUCCESS" | "FAILED" | "SKIPPED";
type EvidenceType = "FACT" | "INFERENCE" | "RECOMMENDATION" | "UNCERTAINTY";
type Evidence = { type: EvidenceType; claim: string; source: string };
type SocietyResult = {
  status: "SUCCESS" | "DEGRADED" | "FALLBACK";
  resume_analysis: { skills: string[]; strengths: Evidence[]; missing_uncertain_areas: Evidence[] } | null;
  fit_analysis: {
    strong_evidence: Evidence[];
    missing_evidence: Evidence[];
    uncertainty: Evidence[];
    fit_assessment: string;
    not_perfect_reason: string;
  } | null;
  interview_analysis: { question: string; category: string; evaluates: string } | null;
  career_strategy: { decision: string; reasoning: string; evidence_used: Evidence[]; confidence: number };
  next_best_action: string;
  verified_sponsorship: { classification: string; evidence_quote?: string | null; source_url?: string | null } | null;
  evidence: Evidence[];
  agent_runs: { agent: string; provider: string; model: string; status: AgentStatus; error?: string | null }[];
  warnings: string[];
};
type JobContext = { title: string; company: string; fitScore: number | null };

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const statusSymbol: Record<AgentStatus, string> = {
  SUCCESS: "✓",
  FAILED: "!",
  SKIPPED: "○",
};

const statusLabel: Record<AgentStatus, string> = {
  SUCCESS: "Complete",
  FAILED: "Unavailable",
  SKIPPED: "Skipped",
};

const confidenceLabel = (confidence: number): string => {
  if (confidence >= 0.7) return "HIGH";
  if (confidence >= 0.4) return "MEDIUM";
  return "LOW";
};

// Concise, decision-useful contribution per agent — built only from fields the API returns.
function agentContribution(agent: string, result: SocietyResult, run: SocietyResult["agent_runs"][number] | undefined): { contribution: string; evidence: Evidence[] } {
  if (!run || run.status !== "SUCCESS") {
    if (run?.status === "SKIPPED") return { contribution: "No interview context supplied.", evidence: [] };
    return { contribution: "This agent's output was unavailable.", evidence: [] };
  }
  switch (agent) {
    case "Resume Analyst": {
      const report = result.resume_analysis;
      return {
        contribution: report?.strengths[0]?.claim ?? "Resume evidence reviewed.",
        evidence: report ? report.strengths.slice(0, 1).concat(report.missing_uncertain_areas.slice(0, 1)) : [],
      };
    }
    case "Fit Critic": {
      const report = result.fit_analysis;
      return {
        contribution: report?.fit_assessment ?? "Fit reviewed.",
        evidence: report ? report.strong_evidence.slice(0, 1).concat(report.missing_evidence.slice(0, 1)) : [],
      };
    }
    case "Interview Agent": {
      const report = result.interview_analysis;
      return {
        contribution: report ? `Asked: "${report.question}" (${report.category})` : "Interview evidence reviewed.",
        evidence: [],
      };
    }
    case "Career Strategist":
      return { contribution: result.career_strategy.reasoning, evidence: result.career_strategy.evidence_used.slice(0, 1) };
    default:
      return { contribution: "", evidence: [] };
  }
}

export function Society() {
  const [result, setResult] = useState<SocietyResult | null>(null);
  const [job, setJob] = useState<JobContext | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [hasResume, setHasResume] = useState(false);
  const [hasJob, setHasJob] = useState(false);

  useEffect(() => {
    setHasResume(Boolean(window.localStorage.getItem("careerpilot_resume_id")));
    setHasJob(Boolean(window.localStorage.getItem("careerpilot_job_id")));
  }, []);

  async function analyze() {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    const jobId = window.localStorage.getItem("careerpilot_job_id");
    const interviewId = window.localStorage.getItem("careerpilot_interview_id");
    setHasResume(Boolean(resumeId));
    setHasJob(Boolean(jobId));
    if (!resumeId) {
      setMessage("Analyze a resume first to run the AI Society.");
      return;
    }

    setBusy(true);
    setMessage("");
    setResult(null);
    try {
      if (jobId) {
        const jobResponse = await fetch(`${apiUrl}/api/jobs/${encodeURIComponent(jobId)}`);
        if (jobResponse.ok) {
          const jobData = await jobResponse.json();
          let fitScore: number | null = null;
          const fitResponse = await fetch(
            `${apiUrl}/api/jobs/${encodeURIComponent(jobId)}/match?resume_id=${encodeURIComponent(resumeId)}`,
          );
          if (fitResponse.ok) fitScore = (await fitResponse.json()).fit_score ?? null;
          setJob({ title: jobData.title, company: jobData.company, fitScore });
        }
      } else {
        setJob(null);
      }

      const response = await fetch(`${apiUrl}/api/society/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_id: resumeId,
          ...(jobId ? { job_id: jobId } : {}),
          ...(interviewId ? { interview_id: interviewId } : {}),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "AI Society could not be reached.");
      setResult(data);
    } catch {
      setMessage("AI Society is temporarily unavailable. Your existing CareerPilot analysis is still available.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rounded-xl border border-indigo-400/30 bg-indigo-400/[0.08] p-5 md:col-span-3" aria-labelledby="society-title">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm text-indigo-200">AI Society</p>
          <h2 id="society-title" className="mt-2 text-xl font-medium">Collaborative career intelligence</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-300">
            Four specialized agents review your evidence and propose one next move. This never submits applications or starts interviews automatically.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void analyze()}
          disabled={busy}
          aria-label="Run AI Society analysis"
          className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? "AI Society is analyzing..." : "Run AI Society"}
        </button>
      </div>

      {busy && <p className="mt-5 text-xs text-indigo-200" role="status">AI Society is analyzing...</p>}
      {!busy && !result && !message && !hasResume && (
        <p className="mt-5 text-xs text-slate-400">Analyze a resume first to run the AI Society.</p>
      )}
      {!busy && !result && !message && hasResume && !hasJob && (
        <p className="mt-5 text-xs text-slate-400">Ready to run resume-only analysis. Job-specific fit analysis unavailable — select a job for a fuller assessment.</p>
      )}
      {message && <p className="mt-5 rounded-lg border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100" role="alert">{message}</p>}
      {job && <p className="mt-5 text-xs text-slate-400">Analyzing: <span className="text-slate-200">{job.title}</span> · {job.company}</p>}

      {result && <SocietyResultView result={result} job={job} />}
    </section>
  );
}

function SocietyResultView({ result, job }: { result: SocietyResult; job: JobContext | null }) {
  const runMap = new Map(result.agent_runs.map((run) => [run.agent, run]));
  const agents = ["Resume Analyst", "Fit Critic", "Interview Agent", "Career Strategist"];
  const overallLabel = result.status === "DEGRADED" ? "Society partially completed" : result.status === "FALLBACK" ? "CareerPilot deterministic fallback used" : "Society completed";
  const evidence = [...result.evidence, ...(result.career_strategy.evidence_used ?? [])].slice(0, 5);

  return (
    <div className="mt-5 space-y-5 border-t border-white/10 pt-5">
      {/* Reasoning trace: shows only agents/statuses actually returned by the API. */}
      <div>
        <p className="text-xs uppercase tracking-wide text-indigo-200">Reasoning trace</p>
        <ol className="mt-3 space-y-0">
          {agents.map((agent, index) => {
            const run = runMap.get(agent);
            const status: AgentStatus = run?.status ?? "SKIPPED";
            const { contribution, evidence: agentEvidence } = agentContribution(agent, result, run);
            return (
              <li key={agent}>
                <div
                  className={`rounded-lg border p-3 ${status === "SUCCESS" ? "border-emerald-300/20 bg-slate-950/25" : status === "SKIPPED" ? "border-white/10 bg-slate-950/15" : "border-amber-300/20 bg-amber-300/[0.06]"}`}
                  aria-label={`${agent}: ${statusLabel[status]}`}
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-200">
                      <span aria-hidden="true">{statusSymbol[status]}</span> {agent}
                    </p>
                    <p className="text-[11px] text-slate-500">{run ? `${run.provider} · ${run.model}` : ""}</p>
                  </div>
                  <p className="mt-1 text-[11px] font-medium text-slate-400">{statusLabel[status]}</p>
                  <p className="mt-2 text-sm text-slate-300">{contribution}</p>
                  {agentEvidence.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {agentEvidence.map((item, itemIndex) => (
                        <p key={`${agent}-${itemIndex}`} className="text-[11px] text-slate-500">
                          <span className="uppercase tracking-wide text-indigo-300">{item.type}</span> · {item.claim}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
                {index < agents.length - 1 && (
                  <p className="my-1 pl-3 text-slate-500" aria-hidden="true">↓</p>
                )}
              </li>
            );
          })}
        </ol>
      </div>

      {job?.fitScore !== null && job?.fitScore !== undefined && (
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg border border-white/10 bg-slate-950/25 p-3">
            <p className="text-[10px] uppercase tracking-wide text-slate-500">CareerPilot Fit (deterministic)</p>
            <p className="mt-1 text-lg font-semibold">{job.fitScore}/100</p>
          </div>
          <div className="rounded-lg border border-indigo-300/20 bg-indigo-950/20 p-3">
            <p className="text-[10px] uppercase tracking-wide text-indigo-300">Society assessment</p>
            <p className="mt-1 text-sm text-slate-300">{result.fit_analysis?.fit_assessment ?? "Not available."}</p>
          </div>
        </div>
      )}

      {/* Prominent final decision panel. */}
      <div className="rounded-lg border border-indigo-300/30 bg-indigo-950/30 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-wide text-indigo-300">Society decision</p>
          <span className={`rounded-full border px-3 py-1 text-xs font-medium ${result.status === "SUCCESS" ? "border-emerald-300/30 text-emerald-200" : "border-amber-300/30 text-amber-200"}`}>
            {result.status}
          </span>
        </div>
        <p className="mt-3 text-[11px] uppercase tracking-wide text-slate-500">Next best action</p>
        <h3 className="mt-1 text-lg font-medium">{result.next_best_action}</h3>
        <p className="mt-3 text-[11px] uppercase tracking-wide text-slate-500">Why</p>
        <p className="mt-1 text-sm text-slate-300">{result.career_strategy.reasoning}</p>
        <p className="mt-3 text-xs text-indigo-200">Confidence: {confidenceLabel(result.career_strategy.confidence)}</p>
        {result.status === "FALLBACK" && (
          <p className="mt-3 rounded-lg border border-amber-300/20 bg-amber-300/10 p-2 text-xs text-amber-100">
            CareerPilot deterministic strategy used because the Society strategist was unavailable.
          </p>
        )}
        {result.status === "DEGRADED" && (
          <p className="mt-3 rounded-lg border border-amber-300/20 bg-amber-300/10 p-2 text-xs text-amber-100">
            {overallLabel}. Some agents were unavailable — see the reasoning trace above.
          </p>
        )}
      </div>

      {/* Verified sponsorship stays authoritative and visually distinct from Society commentary. */}
      <div className="rounded-lg border border-white/10 bg-slate-950/20 p-4">
        <p className="text-[10px] uppercase tracking-wide text-slate-500">Verified sponsorship</p>
        <p className="mt-1 text-sm font-medium">{result.verified_sponsorship?.classification ?? "Not available"}</p>
        {result.verified_sponsorship?.evidence_quote && (
          <>
            <p className="mt-3 text-[10px] uppercase tracking-wide text-slate-500">Source evidence</p>
            <p className="mt-1 text-xs text-slate-400">“{result.verified_sponsorship.evidence_quote}”</p>
          </>
        )}
        <p className="mt-3 text-[10px] uppercase tracking-wide text-indigo-300">Society interpretation</p>
        <p className="mt-1 text-sm text-slate-300">
          {result.fit_analysis?.uncertainty[0]?.claim ??
            (result.verified_sponsorship?.classification === "UNCLEAR" ? "Verify sponsorship before applying." : "No additional commentary.")}
        </p>
        <p className="mt-1 text-[10px] uppercase tracking-wide text-indigo-300">RECOMMENDATION</p>
      </div>

      {evidence.length > 0 && (
        <div>
          <h3 className="text-sm font-medium">Evidence used</h3>
          <div className="mt-3 grid gap-2 md:grid-cols-2">
            {evidence.map((item, index) => (
              <div key={`${item.claim}-${index}`} className="rounded-lg border border-white/10 p-3">
                <p className="text-[10px] uppercase tracking-wide text-indigo-300">{item.type}</p>
                <p className="mt-1 text-sm text-slate-300">{item.claim}</p>
                <p className="mt-2 text-[11px] text-slate-500">Source: {item.source}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.warnings.length > 0 && (
        <div className="rounded-lg border border-amber-300/20 bg-amber-300/10 p-3">
          <p className="text-xs font-medium text-amber-100">Warnings</p>
          <ul className="mt-2 space-y-1 text-xs text-amber-100">
            {result.warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
