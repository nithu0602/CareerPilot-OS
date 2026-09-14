"use client";

import { useState } from "react";

type Session = { interview_id: string; job_title: string; company: string; current_question: { question: string; competency: string; question_type: string }; status: string };
type Reply = { evaluation: { score: number; strengths: string[]; weaknesses: string[]; feedback: string; adaptive: boolean }; next_question: Session["current_question"] | null; progress: number; status: string };
type Results = { average_score: number; overall_assessment: string; strengths: string[]; weaknesses: string[]; recommended_improvements: string[]; suggested_next_action: string };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function Interview({ onNavigate }: { onNavigate?: (tab: "Resume" | "Job Intelligence" | "Interview" | "Applications" | "AI Society") => void }) {
  const [session, setSession] = useState<Session | null>(null);
  const [question, setQuestion] = useState<Session["current_question"] | null>(null);
  const [answer, setAnswer] = useState("");
  const [reply, setReply] = useState<Reply | null>(null);
  const [results, setResults] = useState<Results | null>(null);
  const [message, setMessage] = useState("Analyze a resume and select a job before starting.");

  async function start() {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    const jobId = window.localStorage.getItem("careerpilot_job_id");
    if (!resumeId || !jobId) { setMessage("Complete resume analysis and select a job first."); return; }
    const response = await fetch(`${apiUrl}/api/interviews/start`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume_id: resumeId, job_id: jobId }) });
    const data = await response.json();
    if (!response.ok) { setMessage(data.detail ?? "Could not start interview."); return; }
    setSession(data); setQuestion(data.current_question); window.localStorage.setItem("careerpilot_interview_id", data.interview_id); setMessage("Personalized interview started.");
  }

  async function submit() {
    if (!session || !answer.trim()) { setMessage("Enter an answer before submitting."); return; }
    const response = await fetch(`${apiUrl}/api/interviews/${session.interview_id}/answer`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ answer }) });
    const data: Reply = await response.json();
    if (!response.ok) { setMessage((data as unknown as { detail?: string }).detail ?? "Could not evaluate answer."); return; }
    setReply(data); setAnswer(""); setQuestion(data.next_question);
    if (data.status === "completed") {
      const resultResponse = await fetch(`${apiUrl}/api/interviews/${session.interview_id}/results`);
      setResults(await resultResponse.json());
    }
  }

  return <section className="rounded-xl border border-white/10 bg-white/[0.03] p-5 md:col-span-3"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm text-indigo-300">Interview Agent</p><h2 className="mt-2 text-xl font-medium">Practice for the selected role</h2><p className="mt-2 text-sm text-slate-400">A short text-only interview personalized to your resume and job context.</p></div><button onClick={start} className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white">Start interview</button></div><p className="mt-4 text-xs text-slate-500">{message}</p>{session && question && !results && <div className="mt-5 space-y-4"><div className="rounded-lg border border-indigo-400/20 bg-indigo-400/10 p-4"><p className="text-xs uppercase text-indigo-200">{session.job_title} · {session.company}</p><p className="mt-3 text-lg">{question.question}</p><p className="mt-2 text-xs text-slate-400">{question.question_type} · {question.competency}</p></div><textarea className="min-h-28 w-full rounded-lg border border-white/10 bg-slate-950/40 p-3 text-sm outline-none" placeholder="Write your answer..." value={answer} onChange={(event) => setAnswer(event.target.value)} /><button onClick={submit} className="rounded-lg bg-white/10 px-4 py-2 text-sm">Submit answer</button>{reply && <div className="rounded-lg border border-white/10 p-4 text-sm"><p>CareerPilot assessment: {reply.evaluation.score}/100</p><p className="mt-2 text-slate-300">{reply.evaluation.feedback}</p><p className="mt-2 text-xs text-indigo-300">{reply.evaluation.adaptive ? "Adaptive follow-up generated from the previous weakness." : "Next question selected for the job competency."}</p></div>}</div>}{results && <div className="mt-5 space-y-3"><p className="text-2xl font-semibold text-indigo-300">{results.average_score}/100 average</p><p className="text-sm text-slate-300">{results.overall_assessment}</p><Insight title="Strengths" items={results.strengths} /><Insight title="Weaknesses" items={results.weaknesses} /><Insight title="Recommended improvements" items={results.recommended_improvements} /><p className="text-sm"><span className="text-slate-500">Next action:</span> {results.suggested_next_action}</p>{onNavigate && <div className="pt-2"><button type="button" onClick={() => onNavigate("AI Society")} className="w-full rounded-lg border border-indigo-400/40 bg-indigo-500/20 px-4 py-2 text-sm font-medium text-indigo-200 hover:bg-indigo-500/30 transition-colors">Deliberate Interview Weaknesses with Career Team →</button></div>}</div>}</section>;
}

function Insight({ title, items }: { title: string; items: string[] }) {
  return <div><h3 className="text-sm font-medium">{title}</h3><ul className="mt-2 space-y-1 text-sm text-slate-300">{items.map((item) => <li key={item}>• {item}</li>)}</ul></div>;
}

