"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import { Banknote, Building2, ChevronRight, MapPin, Send, Sparkles } from "lucide-react";
import {
  apiUrl,
  SPECIALISTS,
  OnboardingHero,
  JobCardInline,
  EvidenceType,
  Evidence,
  SpecialistPerspective,
  ChatMessage,
  JobCardData,
  ResumeProfile,
  Tab,
} from "./society-shared";

type JobContext = {
  jobId: string;
  title: string;
  company: string;
  fitScore: number | null;
  sponsorship?: string | null;
  deadline?: string | null;
};

export function SocietyMain({ onNavigate }: { onNavigate?: (tab: Tab) => void }) {
  const [hasResume, setHasResume] = useState<boolean | null>(null);
  const [uploading, setUploading] = useState(false);
  const [resumeProfile, setResumeProfile] = useState<ResumeProfile | null>(null);
  const [job, setJob] = useState<JobContext | null>(null);
  const [hasInterview, setHasInterview] = useState(false);
  const [interviewId, setInterviewId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [deliberating, setDeliberating] = useState(false);
  const [nextBestAction, setNextBestAction] = useState<string | null>(null);
  const [actionReasoning, setActionReasoning] = useState<string | null>(null);
  const [actionCta, setActionCta] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [searchedJobs, setSearchedJobs] = useState<JobCardData[]>([]);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, deliberating]);

  useEffect(() => {
    void initializeContext();
  }, []);

  function profileFromAnalysis(analysisData: Record<string, unknown>): ResumeProfile {
    const profile = (analysisData.profile ?? {}) as Record<string, unknown>;
    return {
      name: (profile.name as string | null) ?? null,
      skills: (profile.skills as string[] | undefined) ?? [],
      strengths: (analysisData.strengths as string[] | undefined) ?? [],
      weaknesses: (analysisData.weaknesses as string[] | undefined) ?? [],
    };
  }

  function profileSummary(analysisData: Record<string, unknown>) {
    const profile = profileFromAnalysis(analysisData);
    const strongestSkills = profile.skills.slice(0, 6).join(", ");
    const strengths = profile.strengths.slice(0, 2).join(" ");
    const gaps = profile.weaknesses.slice(0, 2).join(" ");
    const lines = [
      `Your career team has reviewed your resume${profile.name ? `, ${profile.name}` : ""}.`,
      strongestSkills ? `Strongest skills detected: ${strongestSkills}.` : null,
      strengths ? `Key strengths: ${strengths}` : null,
      gaps ? `Key opportunities: ${gaps}` : "Key opportunities: add measurable project and impact evidence where possible.",
      "I can help you find suitable roles, understand your fit, prepare for interviews, or decide what to do next.",
    ].filter(Boolean) as string[];
    return lines.join("\n\n");
  }

  function clientFallbackReply(message: string, jobCards: JobCardData[]): string {
    const lower = message.toLowerCase();
    const skills = resumeProfile?.skills ?? [];
    const weaknesses = resumeProfile?.weaknesses ?? [];
    const skillSummary = skills.slice(0, 3).join(", ") || "your documented skills";
    const weakness = weaknesses[0] ?? "add measurable evidence to your resume";

    if (/(find jobs|find me|what jobs|recommend jobs|job match|roles fit)/.test(lower)) {
      return jobCards.length
        ? `Here are matching roles from the available CareerPilot jobs. Select a card to review the role or run its fit analysis.`
        : `I couldn't retrieve job cards just now. Your current profile signals are ${skillSummary}; try Job Intelligence to browse the available roles.`;
    }
    if (/(project|portfolio|what should i build|side project)/.test(lower)) {
      return `Build a focused project around ${skillSummary} that closes this current weakness: ${weakness}. Tie it to the target role${job ? `, ${job.title}` : ""} and quantify the outcome in your resume.`;
    }
    if (/(should i apply|apply anyway|apply yet|why shouldn't)/.test(lower)) {
      return job
        ? `For ${job.title} at ${job.company}, your current fit is ${job.fitScore ?? "not yet calculated"}${job.fitScore !== null ? "/100" : ""}. Review the missing requirements before applying${job.sponsorship ? `; sponsorship is currently marked ${job.sponsorship}` : " and verify sponsorship directly with the employer"}.`
        : `Choose a job and run its fit analysis before applying; that will ground the decision in requirements, gaps, and sponsorship evidence.`;
    }
    if (/(100%|why am i not|why not 100|fit score)/.test(lower)) {
      return job
        ? `A perfect match is not expected. ${job.title} is currently ${job.fitScore ?? "not yet calculated"}${job.fitScore !== null ? "/100" : ""}; open its fit analysis to see the specific missing and partial requirements.`
        : `Select a job and run its fit analysis to see the exact missing and partial requirements behind its score.`;
    }
    if (/(fix first|improve resume|fix resume|resume gap|strengthen)/.test(lower)) {
      return `Fix this first: ${weakness}. Then make the supporting experience or project evidence specific and measurable.`;
    }
    if (/(interview|practice|communication)/.test(lower)) {
      return `Use a structured STAR example that demonstrates ${skillSummary}, with a concrete result. Review your interview feedback for the next targeted weakness.`;
    }
    return `Based on your CareerPilot profile, focus on ${skillSummary} while strengthening ${weakness}. Ask about resume improvements, fit, projects, applications, jobs, or interviews for a targeted answer.`;
  }

  function showProfileSummary(analysisData: Record<string, unknown>) {
    const profile = profileFromAnalysis(analysisData);
    setResumeProfile(profile);
    setMessages([
      {
        id: "profile-summary",
        role: "assistant",
        content: profileSummary(analysisData),
        specialist_perspectives: [
          {
            agent: "Resume Analyst",
            perspective: profile.skills.length > 0 ? `Skill signals extracted: ${profile.skills.slice(0, 4).join(", ")}.` : "Resume parsed; skill signals are limited.",
            status: "SUPPORTING",
            evidence_type: "FACT",
          },
        ],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  }

async function initializeContext() {
  const resumeId = window.localStorage.getItem("careerpilot_resume_id");
  const jobId = window.localStorage.getItem("careerpilot_job_id");
  const interviewId = window.localStorage.getItem("careerpilot_interview_id");

  let validInterviewId = interviewId;

  if (interviewId) {
    try {
      const interviewRes = await fetch(
        `${apiUrl}/api/interviews/${encodeURIComponent(interviewId)}/results`,
      );

      if (!interviewRes.ok) {
        validInterviewId = null;
        window.localStorage.removeItem("careerpilot_interview_id");
      }
    } catch {
      validInterviewId = null;
      window.localStorage.removeItem("careerpilot_interview_id");
    }
  }

  setHasResume(Boolean(resumeId));
  setHasInterview(Boolean(validInterviewId));
  setInterviewId(validInterviewId);

  if (!resumeId) return;

  try {
    const analysisRes = await fetch(
      `${apiUrl}/api/resumes/${encodeURIComponent(resumeId)}`,
    );

    if (analysisRes.ok) {
      const data = await analysisRes.json();
      showProfileSummary(data);
    }
  } catch {
    setErrorMessage("");
  }

  let jobCtx: JobContext | null = null;

  if (jobId) {
    try {
      const jobRes = await fetch(
        `${apiUrl}/api/jobs/${encodeURIComponent(jobId)}`,
      );

      if (jobRes.ok) {
        const jobData = await jobRes.json();

        let fitScore: number | null = null;
        let sponsorship: string | null = null;

        const fitRes = await fetch(
          `${apiUrl}/api/jobs/${encodeURIComponent(jobId)}/match?resume_id=${encodeURIComponent(resumeId)}`,
        );

        if (fitRes.ok) {
          const fitData = await fitRes.json();
          fitScore = fitData.fit_score ?? null;
          sponsorship = fitData.sponsorship?.classification ?? null;
        }

        jobCtx = {
          jobId,
          title: jobData.title,
          company: jobData.company,
          fitScore,
          sponsorship,
          deadline: jobData.deadline,
        };

        setJob(jobCtx);
      }
    } catch {
      setErrorMessage("");
    }
  }

  await runInitialBriefing(
    resumeId,
    jobId,
    validInterviewId,
    jobCtx,
  );
}

  async function handleResumeUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setErrorMessage("");
    const form = new FormData();
    form.append("file", file);
    try {
      const uploadRes = await fetch(`${apiUrl}/api/resumes/upload`, { method: "POST", body: form });
      const uploaded = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(uploaded.detail ?? "Upload failed.");
      const analysisRes = await fetch(`${apiUrl}/api/resumes/${uploaded.resume_id}/analyze`, { method: "POST" });
      const analysisData = await analysisRes.json();
      if (!analysisRes.ok) throw new Error(analysisData.detail ?? "Analysis failed.");
      window.localStorage.setItem("careerpilot_resume_id", uploaded.resume_id);
      showProfileSummary(analysisData);
      setHasResume(true);
      await runInitialBriefing(uploaded.resume_id, null, null, null);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Resume analysis failed. Please try again.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function runInitialBriefing(
    resumeId: string,
    jobId: string | null,
    interviewId: string | null,
    jobCtx: JobContext | null,
  ) {
    setDeliberating(true);
    setErrorMessage("");
    try {
      const briefingMessage = jobCtx?.fitScore !== null && jobCtx
        ? `The Fit Agent has already assessed this role. Do not re-run a broad analysis. Acknowledge the existing fit score of ${jobCtx.fitScore}/100 for ${jobCtx.title} at ${jobCtx.company}, highlight the key gaps, and invite the candidate to challenge or discuss the result.`
        : jobId
          ? "Review the candidate's resume and selected role evidence. Deliver the team's opening briefing."
          : "Review the candidate's uploaded resume profile and provide a concise opening career strategy briefing.";
      const response = await fetch(`${apiUrl}/api/society/deliberate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_id: resumeId,
          ...(jobId ? { job_id: jobId } : {}),
          ...(interviewId ? { interview_id: interviewId } : {}),
          message: briefingMessage,
          history: [],
        }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail ?? "Career team deliberation failed.");
      }
      const data = await response.json();
      const initialMessage: ChatMessage = {
        id: "briefing-1",
        role: "assistant",
        content: data.reply,
        specialist_perspectives: data.specialist_perspectives,
        evidence_used: data.evidence_used,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => {
        const profileSummaryMessage = prev.filter((message) => message.id === "profile-summary");
        return [...profileSummaryMessage, initialMessage];
      });
      setNextBestAction(data.next_best_action);
      setActionReasoning(data.reasoning);
      setActionCta(data.action_cta);
    } catch {
      const fallbackReply = jobCtx?.fitScore !== null && jobCtx
        ? `I've reviewed the Fit Agent's assessment of ${jobCtx.title} at ${jobCtx.company}.\n\nYour current fit is ${jobCtx.fitScore}/100.`
        : "I've reviewed your resume profile. The career team is ready to discuss your strengths, career directions, and target opportunities.";
      setMessages((prev) => {
        const profileSummaryMessage = prev.filter((message) => message.id === "profile-summary");
        return [
          ...profileSummaryMessage,
          {
            id: "briefing-fallback",
            role: "assistant",
            content: fallbackReply,
            specialist_perspectives: [
              { agent: "Resume Analyst", perspective: "Profile evidence extracted.", status: "SUPPORTING", evidence_type: "FACT" },
              { agent: "Career Strategist", perspective: "Grounded recommendation initialised.", status: "SUPPORTING", evidence_type: "RECOMMENDATION" },
            ],
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ];
      });
      setNextBestAction(jobCtx ? "Review required skills and prepare application talking points." : "Explore matching jobs in Job Intelligence.");
      setActionReasoning("Baseline evidence initialised.");
      setActionCta(jobCtx ? "PREPARE_APPLICATION" : "JOB_MATCH");
    } finally {
      setDeliberating(false);
    }
  }

  async function searchJobsForChat(query?: string): Promise<JobCardData[]> {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    try {
      const response = await fetch(`${apiUrl}/api/jobs/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: "data analyst",
          location: "",
          keyword: "",
          mode: "demo",
          category: "DATA",
          experience: "GRADUATE",
          work_mode: "ANY",
        }),
      });
      if (!response.ok) return [];
      const data = await response.json();
      const rawJobs = (data.jobs as Record<string, unknown>[] | undefined) ?? [];
      const cards = await Promise.all(
        rawJobs.slice(0, 5).map(async (jobRecord) => {
          let fitScore: number | null = null;
          let sponsorship: string | null = null;
          if (resumeId) {
            try {
              const fitResponse = await fetch(`${apiUrl}/api/jobs/${encodeURIComponent(String(jobRecord.job_id))}/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ resume_id: resumeId }),
              });
              if (fitResponse.ok) {
                const fitData = await fitResponse.json();
                fitScore = fitData.fit_score ?? null;
                sponsorship = fitData.sponsorship?.classification ?? null;
              }
            } catch {
              fitScore = null;
            }
          }
          return {
            job_id: String(jobRecord.job_id),
            title: String(jobRecord.title ?? "Untitled role"),
            company: String(jobRecord.company ?? "Company"),
            location: String(jobRecord.location ?? "United Kingdom"),
            salary: (jobRecord.salary as string | undefined) ?? null,
            fit_score: fitScore,
            sponsorship: sponsorship ?? (jobRecord.sponsorship_information as string | undefined),
            deadline: (jobRecord.deadline as string | undefined) ?? null,
            category: (jobRecord.category as string | undefined) ?? "DATA",
            work_mode: (jobRecord.work_mode as string | undefined) ?? "ANY",
            mode: data.mode,
          } satisfies JobCardData;
        }),
      );
      setSearchedJobs(cards);
      return cards;
    } catch {
      return [];
    }
  }

  function jobForQuestion(question: string, cards: JobCardData[]): JobCardData | null {
    if (!cards.length) return null;
    const lower = question.toLowerCase();
    const location = ["london", "manchester", "birmingham", "leeds", "edinburgh"].find((city) => lower.includes(city));
    if (location) return cards.find((card) => card.location.toLowerCase().includes(location)) ?? cards[0];
    if (lower.includes("which is best") || lower.includes("best")) return [...cards].sort((a, b) => (b.fit_score ?? -1) - (a.fit_score ?? -1))[0];
    return cards[0];
  }

  async function handleAnalyzeFit(jobId: string) {
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    if (!resumeId) return;
    const selected = searchedJobs.find((item) => item.job_id === jobId);
    setDeliberating(true);
    setErrorMessage("");
    try {
      const response = await fetch(`${apiUrl}/api/jobs/${encodeURIComponent(jobId)}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_id: resumeId }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail ?? "Fit analysis failed.");
      }
      const fitData = await response.json();
      const fitJob: JobContext = {
        jobId,
        title: selected?.title ?? job?.title ?? String(fitData.job_id),
        company: selected?.company ?? job?.company ?? "Selected role",
        fitScore: fitData.fit_score ?? null,
        sponsorship: fitData.sponsorship?.classification ?? null,
        deadline: fitData.deadline ?? null,
      };
      setJob(fitJob);
      window.localStorage.setItem("careerpilot_job_id", jobId);
      const whyMatch = (fitData.why_this_match as string[] | undefined) ?? [];
      const whyNot = (fitData.why_not_100 as string[] | undefined) ?? [];
      const grokExplanation = typeof fitData.grok_explanation === "string" && fitData.grok_explanation ? `\n\n${fitData.grok_explanation}` : "";
      setMessages((prev) => [
        ...prev,
        {
          id: `fit-${jobId}-${Date.now()}`,
          role: "assistant",
          content: `Fit analysis for ${fitJob.title} at ${fitJob.company}: ${fitJob.fitScore ?? "pending"}/100.\n\nWhy this match:\n${whyMatch.map((item) => `• ${item}`).join("\n") || "The deterministic engine found no direct overlap yet."}\n\nWhy it is not 100%:\n${whyNot.map((item) => `• ${item}`).join("\n") || "No additional deductions were recorded."}${grokExplanation}`,
          specialist_perspectives: [
            {
              agent: "Fit Critic",
              perspective: `Deterministic fit is ${fitJob.fitScore ?? "pending"}/100. Required and preferred skill evidence remains authoritative.`,
              status: fitJob.fitScore !== null && fitJob.fitScore >= 70 ? "SUPPORTING" : "CHALLENGED",
              evidence_type: "FACT",
            },
          ],
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setNextBestAction(fitData.recommended_next_step ?? "Review the structured fit evidence.");
      setActionReasoning("Fit facts are grounded in the CareerPilot deterministic engine.");
      setActionCta("PREPARE_APPLICATION");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Fit analysis failed.");
    } finally {
      setDeliberating(false);
    }
  }

  function handleJobSelect(selectedJob: JobCardData) {
    setJob({
      jobId: selectedJob.job_id,
      title: selectedJob.title,
      company: selectedJob.company,
      fitScore: selectedJob.fit_score ?? null,
      sponsorship: selectedJob.sponsorship ?? null,
      deadline: selectedJob.deadline ?? null,
    });
    window.localStorage.setItem("careerpilot_job_id", selectedJob.job_id);
  }

  async function sendMessage(textToSend?: string) {
    const messageText = (textToSend ?? input).trim();
    if (!messageText || deliberating) return;
    const resumeId = window.localStorage.getItem("careerpilot_resume_id");
    if (!resumeId) {
      setErrorMessage("Please upload your resume first.");
      return;
    }

    const lowerMessage = messageText.toLowerCase();
    const asksForJobs = ["find jobs", "find me a job", "find me jobs", "what jobs", "jobs fit", "what roles", "recommend roles", "recommend jobs", "job match", "graduate data"].some((term) => lowerMessage.includes(term));
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: messageText,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setDeliberating(true);
    setErrorMessage("");

    let jobCards: JobCardData[] = [];
    if (asksForJobs) {
      jobCards = await searchJobsForChat(messageText);
      const selectedJob = jobForQuestion(messageText, jobCards);
      if (selectedJob) {
        handleJobSelect(selectedJob);
      }
    }

    try {
      const activeJobId = asksForJobs ? jobForQuestion(messageText, jobCards)?.job_id : job?.jobId;
      const response = await fetch(`${apiUrl}/api/society/deliberate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_id: resumeId,
          ...(activeJobId ? { job_id: activeJobId } : {}),
        ...(interviewId ? { interview_id: interviewId } : {}),
        message: messageText,
        history: [...messages, userMessage].map((message) => ({
          role: message.role,
          content: message.job_cards?.length
            ? `${message.content}\n\nPreviously recommended jobs: ${message.job_cards.map((card) => `${card.title} at ${card.company} in ${card.location} (fit ${card.fit_score ?? "not calculated"}/100; sponsorship ${card.sponsorship ?? "not verified"})`).join("; ")}`
            : message.content,
          timestamp: new Date().toISOString(),
        })),
        }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail ?? "Deliberation failed.");
      }
      const data = await response.json();
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.reply,
        specialist_perspectives: data.specialist_perspectives,
        evidence_used: data.evidence_used,
        job_cards: asksForJobs ? jobCards : undefined,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setNextBestAction(data.next_best_action);
      setActionReasoning(data.reasoning);
      setActionCta(data.action_cta);
    } catch {
      const grounded = clientFallbackReply(messageText, jobCards);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-fallback-${Date.now()}`,
          role: "assistant",
          content: grounded,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setDeliberating(false);
    }
  }

  if (hasResume === null) {
    return <section className="rounded-xl border border-white/10 bg-white/[0.03] p-8 md:col-span-3 text-center"><p className="text-sm text-slate-500 animate-pulse">Loading career team…</p></section>;
  }
  if (hasResume === false) {
    return <OnboardingHero onUpload={handleResumeUpload} />;
  }

  const suggestedQuestions = job
    ? ["Why shouldn't I apply yet?", "Why am I not a 100% match?", "What should I fix first?", "Should I apply anyway?", "What projects must I do?", ...(job.sponsorship ? ["Is sponsorship a blocker?"] : []), ...(hasInterview ? ["How can I improve on my interview weakness?"] : [])]
    : ["What roles fit me best?", "Find jobs for me", "What are my biggest gaps?", "How can I improve my resume?", "What projects should I build?"];

  return (
    <section className="rounded-xl border border-indigo-400/20 bg-slate-950/40 p-5 md:col-span-3 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/10 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-indigo-500/20 px-2 py-0.5 text-xs font-semibold uppercase tracking-wider text-indigo-300">AI Society</span>
            <span className="text-xs text-slate-500">Career Reasoning Workspace</span>
          </div>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-100">Talk to your career team</h2>
          <p className="mt-1 text-sm text-slate-400">Ask a career question, challenge the evidence, or discover your next move.</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 text-right min-w-[13rem]">
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
              <button type="button" onClick={() => onNavigate?.("Job Intelligence")} className="mt-1 text-[11px] text-indigo-300 hover:underline">Select a job for specific fit →</button>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {SPECIALISTS.map((specialist) => (
          <div key={specialist.name} className="flex items-center gap-2.5 rounded-lg border border-white/5 bg-white/[0.02] p-2.5">
            <span className="text-base" aria-hidden="true">{specialist.icon}</span>
            <div className="min-w-0"><p className="truncate text-xs font-medium text-slate-200">{specialist.name}</p><p className="truncate text-[10px] text-slate-500">{specialist.role}</p></div>
          </div>
        ))}
      </div>

      <div className="space-y-4 rounded-xl border border-white/10 bg-slate-950/60 p-4 min-h-[320px] max-h-[500px] overflow-y-auto">
        {messages.map((message) => (
          <div key={message.id} className={`flex flex-col ${message.role === "user" ? "items-end" : "items-start"}`}>
            <div className="mb-1 flex items-center gap-1.5 px-1 text-[11px] text-slate-500">
              <span>{message.role === "user" ? "You" : "Career Team (Society)"}</span><span>· {message.timestamp}</span>
            </div>
            <div className={`rounded-xl px-4 py-3 text-sm leading-relaxed max-w-[88%] ${message.role === "user" ? "bg-indigo-500/15 text-indigo-50" : "bg-white/[0.04] text-slate-200"}`}>
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.job_cards && message.job_cards.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <p className="mb-2 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-indigo-300"><Sparkles className="h-3 w-3" /> Recommended Roles</p>
                  {message.job_cards.map((jobCard) => <JobCardInline key={jobCard.job_id} job={jobCard} onSelect={handleJobSelect} onAnalyzeFit={handleAnalyzeFit} />)}
                </div>
              )}
              {message.specialist_perspectives && message.specialist_perspectives.length > 0 && (
                <div className="mt-3 space-y-2 border-t border-white/10 pt-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-indigo-300">Specialist Conclusions</p>
                  <div className="space-y-1.5">
                    {message.specialist_perspectives.map((perspective, idx) => (
                      <div key={`${perspective.agent}-${idx}`} className="rounded-lg border border-white/5 bg-slate-950/40 p-2 text-xs">
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-medium text-slate-300">{perspective.agent}</span>
                          <span className={`rounded px-1.5 py-0.5 text-[9px] font-semibold uppercase ${perspective.status === "ADJUSTED" ? "bg-indigo-500/20 text-indigo-200 border border-indigo-400/30" : perspective.status === "CHALLENGED" ? "bg-amber-500/20 text-amber-200 border border-amber-400/30" : "bg-emerald-500/15 text-emerald-300"}`}>{perspective.status}</span>
                        </div>
                        <p className="mt-1 text-slate-400 leading-normal">{perspective.perspective}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {message.evidence_used && message.evidence_used.length > 0 && (
                <div className="mt-2.5 flex flex-wrap gap-1.5 pt-1 text-[10px] text-slate-500">
                  {message.evidence_used.map((evidence, evIdx) => <span key={evIdx} className="rounded bg-white/5 px-2 py-0.5 text-slate-400" title={evidence.source}><strong className="text-indigo-300 uppercase">{evidence.type}</strong>: {evidence.claim}</span>)}
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
          {suggestedQuestions.map((question) => (
            <button key={question} type="button" onClick={() => void sendMessage(question)} disabled={deliberating} className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-300 hover:border-indigo-400/50 hover:bg-indigo-500/10 transition-all disabled:opacity-50">{question}</button>
          ))}
        </div>
      </div>

      <form onSubmit={(event) => { event.preventDefault(); void sendMessage(); }} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask or challenge the career team…"
          disabled={deliberating}
          className="flex-1 rounded-lg border border-white/10 bg-slate-950/60 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-indigo-400/60 transition-colors disabled:opacity-50"
        />
        <button type="submit" disabled={!input.trim() || deliberating} className="rounded-lg bg-indigo-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-400 transition-colors disabled:cursor-not-allowed disabled:opacity-50 shadow-md shadow-indigo-500/20">
          {deliberating ? "Deliberating…" : <span className="inline-flex items-center gap-1.5">Send <Send className="h-3.5 w-3.5" /></span>}
        </button>
      </form>

      {nextBestAction && (
        <div className="rounded-xl border border-indigo-400/30 bg-indigo-950/25 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-indigo-400/15 pb-2.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300">Next Best Action</span>
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
}
