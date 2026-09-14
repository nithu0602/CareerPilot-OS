"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Building2, MapPin, Banknote, ChevronRight, Briefcase } from "lucide-react";
import { apiUrl, SPECIALISTS, OnboardingHero, OnboardingAnalyzed, JobCardInline, type EvidenceType, type Evidence, type SpecialistPerspective, type ChatMessage, type JobCardData, type ResumeProfile, type Tab } from "./society-shared";

export function SocietyMain({ onNavigate }: { onNavigate?: (tab: Tab) => void }) {
  const [hasResume, setHasResume] = useState<boolean | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [resumeProfile, setResumeProfile] = useState<ResumeProfile | null>(null);
  const [job, setJob] = useState<{ jobId: string; title: string; company: string; fitScore: number | null; sponsorship?: string | null; deadline?: string | null } | null>(null);
  const [hasInterview, setHasInterview] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [deliberating, setDeliberating] = useState(false);
  const [nextBestAction, setNextBestAction] = useState<string | null>(null);
  const [actionReasoning, setActionReasoning] = useState<string | null>(null);
  const [actionCta, setActionCta] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [searchedJobs, setSearchedJobs] = useState<JobCardData[]>([]);

  const chatEndRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, deliberating]);
  useEffect(() => { void initializeContext(); // eslint-disable-next-line react-hooks/exhaustive-deps }, []);

  async function initializeContext() {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    const jobId = window.localStorage.getItem("careerpilot_job_id");
    const interviewId = window.localStorage.getItem("careerpilot_interview_id");
    setHasResume(Boolean(resumeId));
    setHasInterview(Boolean(interviewId));
    if (!resumeId) return;
    try {
      const analysisRes = await fetch(`${apiUrl}/api/resumes/${encodeURIComponent(resumeId)}/analysis`);
      if (analysisRes.ok) {
        const data = await analysisRes.json();
        setResumeProfile({ name: data.profile?.name ?? null, skills: data.profile?.skills ?? [], strengths: data.strengths ?? [], weaknesses: data.weaknesses ?? [] });
      }
    } catch { /* Non-fatal */ }
    let jobCtx: { jobId: string; title: string; company: string; fitScore: number | null; sponsorship?: string | null; deadline?: string | null } | null = null;
    if (jobId) {
      try {
        const jobRes = await fetch(`${apiUrl}/api/jobs/${encodeURIComponent(jobId)}`);
        if (jobRes.ok) {
          const jobData = await jobRes.json();
          let fitScore: number | null = null;
          let sponsorship: string | null = null;
          const fitRes = await fetch(`${apiUrl}/api/jobs/${encodeURIComponent(jobId)}/match?resume_id=${encodeURIComponent(resumeId)}`);
          if (fitRes.ok) { const fitData = await fitRes.json(); fitScore = fitData.fit_score ?? null; sponsorship = fitData.sponsorship?.classification ?? null; }
          jobCtx = { jobId, title: jobData.title, company: jobData.company, fitScore, sponsorship, deadline: jobData.deadline };
          setJob(jobCtx);
        }
      } catch { /* Graceful */ }
    }
    await runInitialBriefing(resumeId, jobId, interviewId, jobCtx);
  }

  async function handleResumeUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus("Uploading…");
    const form = new FormData();
    form.append("file", file);
    try {
      const uploadRes = await fetch(`${apiUrl}/api/resumes/upload`, { method: "POST", body: form });
      const uploaded = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(uploaded.detail ?? "Upload failed.");
      setUploadStatus("Analyzing…");
      const analysisRes = await fetch(`${apiUrl}/api/resumes/${uploaded.resume_id}/analyze`, { method: "POST" });
      const analysisData = await analysisRes.json();
      if (!analysisRes.ok) throw new Error(analysisData.detail ?? "Analysis failed.");
      window.localStorage.setItem("careerpilot_resume_id", uploaded.resume_id);
      setResumeProfile({ name: analysisData.profile?.name ?? null, skills: analysisData.profile?.skills ?? [], strengths: analysisData.strengths ?? [], weaknesses: analysisData.weaknesses ?? [] });
      setHasResume(true);
      setUploadStatus("");
      showProfileSummary(analysisData);
      await runInitialBriefing(uploaded.resume_id, null, null, null);
    } catch (err) { setUploadStatus(err instanceof Error ? err.message : "Resume upload failed."); }
    finally { setUploading(false); event.target.value = ""; }
  }

  function handleContinue() { setHasResume(true); void initializeContext(); }

  function showProfileSummary(analysisData: Record<string, unknown>) {
    const profile = analysisData.profile as Record<string, object> | undefined;
    const skills = (profile?.skills as string[] | undefined) ?? [];
    const strengths = (analysisData.strengths as string[] | undefined) ?? [];
    const weaknesses = (analysisData.weaknesses as string[] | undefined) ?? [];
    const name = profile?.name as string | null;
    const summaryContent = [
      `Your career team has reviewed your resume${name ? `, ${name}` : ""}.`,
      "",
      skills.length > 0 ? `**Strengths detected:** ${skills.slice(0, 6).join(", ")}` : null,
      strengths.length > 0 ? `**Evidence highlights:** ${strengths[0]}` : null,
      weaknesses.length > 0 ? `**Potential gaps:** ${weaknesses.slice(0, 2).join("; ")}` : null,
    ].filter(Boolean).join("\n");
    setMessages([{ id: "profile-summary", role: "assistant", content: summaryContent, specialist_perspectives: [{ agent: "Resume Analyst", perspective: skills.length > 0 ? `Skill signals extracted: ${skills.slice(0, 4).join(", ")}.` : "Resume parsed.", status: "SUPPORTING", evidence_type: "FACT" }], timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]);
  }

  async function runInitialBriefing(resumeId: string, jobId: string | null, interviewId: string | null, jobCtx: { jobId: string; title: string; company: string; fitScore: number | null; sponsorship?: string | null; deadline?: string | null } | null) {
    setDeliberating(true); setErrorMessage("");
    try {
      const briefingMessage = jobCtx?.fitScore !== null && jobCtx
        ? `The Fit Agent has already assessed this role. Do NOT re-run a broad analysis. Instead: acknowledge the existing fit score of ${jobCtx.fitScore}/100 for ${jobCtx.title} at ${jobCtx.company}, highlight the key gaps, and invite the candidate to challenge or discuss the result.`
        : jobId ? "Review the candidate's resume and selected role evidence. Deliver the team's opening briefing." : "Review the candidate's uploaded resume profile and provide the team's opening career strategy briefing. Be concise.";
      const response = await fetch(`${apiUrl}/api/society/deliberate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume_id: resumeId, ...(jobId ? { job_id: jobId } : {}), ...(interviewId ? { interview_id: interviewId } : {}), message: briefingMessage, history: [] }) });
      if (!response.ok) { const err = await response.json(); throw new Error(err.detail ?? "Career team deliberation failed."); }
      const data = await response.json();
      const initialMessage: ChatMessage = { id: "briefing-1", role: "assistant", content: data.reply, specialist_perspectives: data.specialist_perspectives, evidence_used: data.evidence_used, timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) };
      setMessages((prev) => { const profSummary = prev.filter((m) => m.id === "profile-summary"); return [...profSummary, initialMessage]; });
      setNextBestAction(data.next_best_action); setActionReasoning(data.reasoning); setActionCta(data.action_cta);
    } catch {
      const fallbackReply = jobCtx?.fitScore !== null && jobCtx ? `I've reviewed the Fit Agent's assessment of ${jobCtx.title} at ${jobCtx.company}.\n\nYour current fit is ${jobCtx.fitScore}/100.` : "I've reviewed your resume profile. The career team is ready to discuss your strengths, career directions, and target opportunities.";
      setMessages((prev) => { const profSummary = prev.filter((m) => m.id === "profile-summary"); return [...profSummary, { id: "briefing-fallback", role: "assistant", content: fallbackReply, specialist_perspectives: [{ agent: "Resume Analyst", perspective: "Profile evidence extracted.", status: "SUPPORTING", evidence_type: "FACT" as EvidenceType }, { agent: "Career Strategist", perspective: "Grounded recommendation initialised.", status: "SUPPORTING", evidence_type: "RECOMMENDATION" as EvidenceType }], timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]; });
      setNextBestAction(jobCtx ? "Review required skills and prepare application talking points." : "Explore matching jobs in Job Intelligence.");
      setActionReasoning("Baseline evidence initialised.");
      setActionCta(jobCtx ? "PREPARE_APPLICATION" : "JOB_MATCH");
    } finally { setDeliberating(false); }
  }

  async function handleJobSearch(query?: string) {
    setDeliberating(true);
    try {
      const response = await fetch(`${apiUrl}/api/jobs/search`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role: query ?? "", location: "", keyword: query ?? "", mode: "demo", category: "DATA", experience: "GRADUATE", work_mode: "ANY" }) });
      if (response.ok) {
        const data = await response.json();
        const cards: JobCardData[] = data.jobs.map((j: Record<string, unknown>) => ({ job_id: j.job_id as string, title: j.title as string, company: j.company as string, location: j.location as string, salary: j.salary as string | undefined, fit_score: null, sponsorship: j.sponsorship_information as string | undefined, deadline: j.deadline as string | undefined, category: j.category as string, work_mode: j.work_mode as string }));
        setSearchedJobs(cards);
      }
    } catch { /* Graceful */ } finally { setDeliberating(false); }
  }

  async function handleAnalyzeFit(jobId: string) {
    try {
      const resumeId = window.localStorage.getItem("careerpilot_resume_id");
      if (!resumeId) return;
      setDeliberating(true);
      const response = await fetch(`${apiUrl}/api/jobs/${encodeURIComponent(jobId)}/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume_id: resumeId }) });
      if (response.ok) { const fitData = await response.json(); setJob({ jobId, title: job?.title ?? "", company: job?.company ?? "", fitScore: fitData.fit_score ?? null, sponsorship: fitData.sponsorship?.classification ?? null, deadline: fitData.deadline ?? null }); }
    } catch { /* Graceful */ } finally { setDeliberating(false); }
  }

  function handleJobSelect(selectedJob: JobCardData) {
    setJob({ jobId: selectedJob.job_id, title: selectedJob.title, company: selectedJob.company, fitScore: selectedJob.fit_score ?? null, sponsorship: selectedJob.sponsorship ?? null, deadline: selectedJob.deadline ?? null });
    window.localStorage.setItem("careerpilot_job_id", selectedJob.job_id);
  }

  async function sendMessage(textToSend?: string) {
    const messageText = (textToSend ?? input).trim();
    if (!messageText || deliberating) return;
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    if (!resumeId) { setErrorMessage("Please upload your resume first."); return; }
    const userMessage: ChatMessage = { id: `user-${Date.now()}`, role: "user", content: messageText, timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) };
    setMessages((prev) => [...prev, userMessage]);
    setInput(""); setDeliberating(true); setErrorMessage("");
    try {
      const response = await fetch(`${apiUrl}/api/society/deliberate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume_id: resumeId, ...(job?.jobId ? { job_id: job.jobId } : {}), message: messageText, history: [...messages, userMessage].map((m) => ({ role: m.role, content: m.content, timestamp: new Date().toISOString() })) }) });
      if (!response.ok) { const err = await response.json(); throw new Error(err.detail ?? "Deliberation failed."); }
      const data = await response.json();
      const lowerMsg = messageText.toLowerCase();
      const asksForJobs = ["find jobs", "find role", "what roles", "job match", "recommend", "graduate data"].some((t) => lowerMsg.includes(t));
      const jobCards: JobCardData[] = asksForJobs && searchedJobs.length > 0 ? searchedJobs : [];
      const assistantMessage: ChatMessage = { id: `assistant-${Date.now()}`, role: "assistant", content: data.reply, specialist_perspectives: data.specialist_perspectives, evidence_used: data.evidence_used, job_cards: jobCards, timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) };
      setMessages((prev) => [...prev, assistantMessage]);
      setNextBestAction(data.next_best_action); setActionReasoning(data.reasoning); setActionCta(data.action_cta);
      if (asksForJobs) setSearchedJobs([]);
    } catch {
      const resumeSkills = resumeProfile?.skills ?? [];
      const grounded = resumeSkills.length > 0 ? `I couldn't complete the full team deliberation, but based on your CareerPilot evidence: your strongest signals are ${resumeSkills.slice(0, 3).join(", ")}.` : "I couldn't complete the full team deliberation. Please upload your resume first.";
      setMessages((prev) => [...prev, { id: `error-fallback-${Date.now()}`, role: "assistant", content: grounded, timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]);
    } finally { setDeliberating(false); }
  }

  if (hasResume === null) {
    return <section className="rounded-xl border border-white/10 bg-white/[0.03] p-8 md:col-span-3 text-center"><p className="text-sm text-slate-500 animate-pulse">Loading career team…</p></section>;
  }
  if (hasResume === false) {
    return <OnboardingHero onUpload={handleResumeUpload} />;
  }

  const suggestedQuestions = job
    ? ["Why shouldn't I apply yet?", "Why am I not a 100% match?", "What should I fix first?", "Should I apply anyway?", "What projects must I do?", ...(job.sponsorship ? ["Is sponsorship a blocker?"] : []), ...(hasInterview ? ["How can I improve on my interview weakness?"] : [])]
    : ["What roles fit me best?", "Find graduate jobs for me", "What are my biggest gaps?", "How can I improve my resume?", "What projects must I do?"];

  return (
    <section className="rounded-xl border border-indigo-400/20 bg-slate-950/40 p-5 md:col-span-3 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/10 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-indigo-500/20 px-2 py-0.5 text-xs font-semibold uppercase tracking-wider text-indigo-300">AI Society</span>
            <span className="text-xs text-slate-500">· Career Reasoning Workspace</span>
          </div>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-100">Talk to your career team</h2>
          <p className="mt-1 text-sm text-slate-400">The specialists analyse evidence; the Society deliberates with you.</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 text-right">
          <p className="text-[11px] uppercase tracking-wider text-slate-500">Active Review Target</p>
          {job ? (
            <div className="mt-1">
              <p className="text-sm font-medium text-slate-200">{job.title}</p>
              <p className="text-xs text-slate-400">{job.company}</p>
              <div className="mt-1.5 flex justify-end gap-1.5">
                {job.fitScore !== null && <span className="rounded-full bg-indigo-500/20 px-2 py-0.5 text-[10px] font-semibold text-indigo-300">{job.fitScore}/100 Fit</span>}
                {job.sponsorship && <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-200 border border-amber-500/20">Sponsorship: {job.sponsorship}</span>}
              </div>
            </div>
          ) : (
            <div className="mt-1">
              <p className="text-sm font-medium text-slate-300">Candidate Profile &amp; Career Direction</p>
              <button type="button" onClick={() => onNavigate?.("Job Intelligence")} className="mt-1 text-[11px] text-indigo-300 hover:underline">+ Select a job to deliberate on specific role fit →</button>
            </div>
          )}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {SPECIALISTS.map((s) => (
          <div key={s.name} className="flex items-center gap-2.5 rounded-lg border border-white/5 bg-white/[0.02] p-2.5">
            <span className="text-base" aria-hidden="true">{s.icon}</span>
            <div className="min-w-0"><p className="truncate text-xs font-medium text-slate-200">{s.name}</p><p className="truncate text-[10px] text-slate-500">{s.role}</p></div>
          </div>
        ))}
      </div>
      <div className="space-y-4 rounded-xl border border-white/10 bg-slate-950/60 p-4 min-h-[320px] max-h-[500px] overflow-y-auto">
        {messages.map((m) => (
          <div key={m.id} className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}>
            <div className="mb-1 flex items-center gap-1.5 px-1 text-[11px] text-slate-500">
              <span>{m.role === "user" ? "You" : "Career Team (Society)"}</span><span>· {m.timestamp}</span>
            </div>
            <div className={`rounded-xl px-4 py-3 text-sm leading-relaxed max-w-[88%] ${m.role === "user" ? "bg-indigo-600 text-white rounded-br-none" : "border border-white/10 bg-slate-900/90 text-slate-200 rounded-bl-none"}`}>
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.job_cards && m.job_cards.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-indigo-300 mb-2">Recommended Roles</p>
                  {m.job_cards.map((j) => <JobCardInline key={j.job_id} job={j} onSelect={handleJobSelect} onAnalyzeFit={handleAnalyzeFit} />)}
                </div>
              )}
              {m.specialist_perspectives && m.specialist_perspectives.length > 0 && (
                <div className="mt-3 space-y-2 border-t border-white/10 pt-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-indigo-300">Specialist Deliberation Breakdown</p>
                  <div className="space-y-1.5">
                    {m.specialist_perspectives.map((p, idx) => (
                      <div key={`${p.agent}-${idx}`} className="rounded-lg border border-white/5 bg-slate-950/40 p-2 text-xs">
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-medium text-slate-300">{p.agent}</span>
                          <span className={`rounded px-1.5 py-0.5 text-[9px] font-semibold uppercase ${p.status === "ADJUSTED" ? "bg-indigo-500/20 text-indigo-200 border border-indigo-400/30" : p.status === "CHALLENGED" ? "bg-amber-500/20 text-amber-200 border border-amber-400/30" : "bg-emerald-500/15 text-emerald-300"}`}>{p.status}</span>
                        </div>
                        <p className="mt-1 text-slate-400 leading-normal">{p.perspective}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {m.evidence_used && m.evidence_used.length > 0 && (
                <div className="mt-2.5 flex flex-wrap gap-1.5 pt-1 text-[10px] text-slate-500">
                  {m.evidence_used.map((ev, evIdx) => <span key={evIdx} className="rounded bg-white/5 px-2 py-0.5 text-slate-400" title={ev.source}><strong className="text-indigo-300 uppercase">{ev.type}</strong>: {ev.claim}</span>)}
                </div>
              )}
            </div>
          </div>
        ))}
        {deliberating && (
          <div className="flex flex-col items-start">
            <div className="rounded-xl border border-indigo-400/20 bg-slate-900/90 px-4 py-3 text-xs text-indigo-200 animate-pulse">Career team is deliberating…</div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      {errorMessage && <p className="rounded-lg border border-amber-300/20 bg-amber-300/10 p-3 text-xs text-amber-200">{errorMessage}</p>}
      <div>
        <p className="mb-2 text-xs text-slate-400">Suggested challenges &amp; inquiries:</p>
        <div className="flex flex-wrap gap-2">
          {suggestedQuestions.map((q) => (
            <button key={q} type="button" onClick={() => void sendMessage(q)} disabled={deliberating} className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-300 hover:border-indigo-400/50 hover:bg-indigo-500/10 transition-all disabled:opacity-50">{q}</button>
          ))}
        </div>
      </div>
      <form onSubmit={(e) => { e.preventDefault(); void sendMessage(); }} className="flex gap-2">
        <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask or challenge the career team…" disabled={deliberating} className="flex-1 rounded-lg border border-white/10 bg-slate-950/60 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-400/60 transition-colors disabled:opacity-50" />
        <button type="submit" disabled={!input.trim() || deliberating} className="rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-400 transition-colors disabled:cursor-not-allowed disabled:opacity-50 shadow-md shadow-indigo-500/20">{deliberating ? "Deliberating…" : "Send"}</button>
      </form>
      {nextBestAction && (
        <div className="rounded-xl border border-indigo-400/30 bg-indigo-950/25 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-indigo-400/15 pb-2.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300">⚡ Next Best Action</span>
            <span className="text-[11px] text-slate-400">Decision</span>
          </div>
          <p className="mt-2.5 text-base font-medium text-slate-100">{nextBestAction}</p>
          {actionReasoning && <p className="mt-1 text-xs text-slate-400">{actionReasoning}</p>}
          {onNavigate && (
            <div className="mt-4 flex flex-wrap gap-2 pt-1 border-t border-white/5">
              {(actionCta === "PREPARE_APPLICATION" || !actionCta) && <button type="button" onClick={() => onNavigate("Applications")} className="rounded-lg bg-indigo-500 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-indigo-400">Prepare Application →</button>}
              {actionCta === "PRACTICE_INTERVIEW" && <button type="button" onClick={() => onNavigate("Interview")} className="rounded-lg bg-indigo-500 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-indigo-400">Practice Interview →</button>}
              {actionCta === "UPDATE_RESUME" && <button type="button" onClick={() => onNavigate("Resume")} className="rounded-lg bg-indigo-500 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-indigo-400">Update Resume →</button>}
              {(actionCta === "JOB_MATCH" || actionCta === "FIND_ROLES") && <button type="button" onClick={() => onNavigate("Job Intelligence")} className="rounded-lg bg-indigo-500 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-indigo-400">Explore Jobs →</button>}
              {job && actionCta !== "PRACTICE_INTERVIEW" && <button type="button" onClick={() => onNavigate("Interview")} className="rounded-lg border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs text-slate-300 hover:bg-white/10">Practice Interview</button>}
            </div>
          )}
        </div>
      )}
    </section>
  );
