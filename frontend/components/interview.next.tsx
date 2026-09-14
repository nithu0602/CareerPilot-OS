"use client";

import { useState } from "react";

type Question = { question: string; competency: string; question_type: string };
type Session = {
  interview_id: string; job_title: string; company: string;
  current_question: Question; status: string; question_number: number; max_questions: number;
};
type CategoryScore = { category: string; average_score: number; question_count: number };
type Reply = {
  evaluation: { score: number; strengths: string[]; weaknesses: string[]; feedback: string; adaptive: boolean };
  next_question: Question | null; progress: number; status: string;
};
type Results = {
  average_score: number; overall_assessment: string; strengths: string[];
  weaknesses: string[]; competencies_assessed: string[]; category_scores: CategoryScore[];
  recommended_improvements: string[]; suggested_next_action: string;
};
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const TYPE_LABELS: Record<string, string> = {
  behavioral: "Behavioural (STAR)", technical: "Technical", project: "Project experience",
  situational: "Scenario", sql_data: "SQL & data analysis", communication: "Stakeholder communication",
  role_competency: "Role competency", motivation: "Motivation & role fit", teamwork: "Teamwork",
  problem_solving: "Problem solving", business_insight: "Business insight",
  reflection: "Feedback & reflection", prioritisation: "Prioritisation",
};

function label(value: string | null | undefined): string {
  if (!value) return "General";
  return TYPE_LABELS[value] ?? value.replace("_", " ");
}

export function Interview({ onNavigate }: { onNavigate?: (tab: "Resume" | "Job Intelligence" | "Interview" | "Applications" | "AI Society") => void }) {
  const [session, setSession] = useState<Session | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
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
    setSession(data); setQuestion(data.current_question); setReply(null); setResults(null);
    window.localStorage.setItem("careerpilot_interview_id", data.interview_id);
    setMessage(`Personalized interview started: ${data.max_questions} questions, chosen adaptively from each answer.`);
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

  const progressWidth = session && session.max_questions > 0 ? (session.question_number / session.max_questions) * 100 : 0;

  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.03] p-5 md:col-span-3">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm text-indigo-300">Interview Agent</p>
          <h2 className="mt-2 text-xl font-medium">Practice for the selected role</h2>
          <p className="mt-2 text-sm text-slate-400">A text-only interview personalized to your resume and job. Each session adapts the next question to your previous answer.</p>
        </div>
        <button onClick={start} className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white">Start interview</button>
      </div>

      <p className="mt-4 text-xs text-slate-500">{message}</p>
{session && question && !results && (
        <div className="mt-5 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400">Question {session.question_number} of {session.max_questions}</p>
            {reply && <p className="text-xs text-slate-400">{reply.progress}% complete</p>}
          </div>
          <div className="h-1 rounded-full bg-white/10">
            <div className="h-1 rounded-full bg-indigo-400" style={{ width: `${progressWidth}%` }} />
          </div>
          <div className="rounded-lg border border-indigo-400/20 bg-indigo-400/10 p-4">
            <p className="text-xs uppercase text-indigo-200">{session.job_title} · {session.company} · {label(question.question_type)}</p>
            <p className="mt-3 text-lg">{question.question}</p>
            <p className="mt-2 text-xs text-slate-400">{question.competency}</p>
          </div>
          <textarea className="min-h-28 w-full rounded-lg border border-white/10 bg-slate-950/40 p-3 text-sm outline-none" placeholder="Write your answer using a specific example and a measurable result..." value={answer} onChange={(event) => setAnswer(event.target.value)} />
          <button onClick={submit} className="rounded-lg bg-white/10 px-4 py-2 text-sm">Submit answer</button>
          {reply && (
            <div className="rounded-lg border border-white/10 p-4 text-sm">
              <p>CareerPilot assessment: <span className="font-medium text-indigo-200">{reply.evaluation.score}/100</span></p>
              <p className="mt-2 text-slate-300">{reply.evaluation.feedback}</p>
              {reply.evaluation.strengths.length > 0 && <ul className="mt-2 space-y-1 text-xs text-emerald-200/80">{reply.evaluation.strengths.map((item) => <li key={`s-${item}`}>+ {item}</li>)}</ul>}
              {reply.evaluation.weaknesses.length > 0 && <ul className="mt-2 space-y-1 text-xs text-amber-200/80">{reply.evaluation.weaknesses.map((item) => <li key={`w-${item}`}>− {item}</li>)}</ul>}
              <p className="mt-2 text-xs text-indigo-300">{reply.evaluation.adaptive ? "Adaptive follow-up generated from the previous weakness." : "Next question selected for the job competency."}</p>
            </div>
          )}
        </div>
      )}

      {results && (
        <div className="mt-5 space-y-4">
          <div className="rounded-lg border border-indigo-400/20 bg-indigo-400/10 p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Overall score</p>
              <p className="text-2xl font-semibold text-indigo-300">{results.average_score}/100</p>
            </div>
            <p className="mt-2 text-xs text-slate-300">based on {results.competencies_assessed.length} competencies across {results.category_scores.length} categories</p>
          </div>
          <p className="text-sm text-slate-300">{results.overall_assessment}</p>

          {results.category_scores.length > 0 && (
            <div>
              <h3 className="text-sm font-medium">Category scores</h3>
              <div className="mt-2 space-y-2">
                {results.category_scores.map((item) => (
                  <div key={item.category}>
                    <div className="flex justify-between text-xs"><span>{label(item.category)}</span><span>{item.average_score}/100 · {item.question_count} q</span></div>
                    <div className="mt-0.5 h-1 rounded-full bg-white/10"><div className="h-1 rounded-full bg-indigo-400" style={{ width: `${item.average_score}%` }} /></div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Insight title="Strength areas" items={results.strengths} accent="text-emerald-200/80" />
          <Insight title="Weakness areas" items={results.weaknesses} accent="text-amber-200/80" />
          <Insight title="Improvement advice" items={results.recommended_improvements} accent="text-slate-300" />
{results.suggested_next_action && (
            <div className="rounded-lg border border-amber-400/20 bg-amber-400/10 p-3 text-sm">
              <p><span className="text-slate-500">Recommended next action: </span>{results.suggested_next_action}</p>
            </div>
          )}

          {onNavigate && (
            <div className="pt-2">
              <button type="button" onClick={() => onNavigate("AI Society")} className="w-full rounded-lg border border-indigo-400/40 bg-indigo-500/20 px-4 py-2.5 text-sm font-medium text-indigo-200 hover:bg-indigo-500/30 transition-colors">Deliberate Interview Weaknesses with Career Team →</button>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function Insight({ title, items, accent }: { title: string; items: string[]; accent: string }) {
  if (!items || items.length === 0) return null;
  return <div><h3 className="text-sm font-medium">{title}</h3><ul className={`mt-2 space-y-1 text-sm ${accent}`}>{items.map((item) => <li key={item}>• {item}</li>)}</ul></div>;
}