"use client";

import { ChangeEvent } from "react";
import { motion } from "framer-motion";
import { Upload, ChevronRight, Building2, MapPin, Banknote } from "lucide-react";

export type EvidenceType = "FACT" | "INFERENCE" | "RECOMMENDATION" | "UNCERTAINTY";
export type Evidence = { type: EvidenceType; claim: string; source: string };

export type SpecialistPerspective = {
  agent: string;
  perspective: string;
  status: "SUPPORTING" | "CHALLENGED" | "ADJUSTED" | "NEUTRAL";
  evidence_type: EvidenceType;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  specialist_perspectives?: SpecialistPerspective[];
  evidence_used?: Evidence[];
  job_cards?: JobCardData[];
  timestamp: string;
};

export type JobCardData = {
  job_id: string;
  title: string;
  company: string;
  location: string;
  salary?: string | null;
  fit_score?: number | null;
  sponsorship?: string | null;
  deadline?: string | null;
  category?: string;
  work_mode?: string;
  mode?: "demo" | "live" | "fallback";
};

export type ResumeProfile = {
  name: string | null;
  skills: string[];
  strengths: string[];
  weaknesses: string[];
};

export type Tab = "Resume" | "Job Intelligence" | "Interview" | "Applications" | "AI Society";

export type JobContext = {
  jobId: string;
  title: string;
  company: string;
  fitScore: number | null;
  sponsorship?: string | null;
  deadline?: string | null;
};

export const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const SPECIALISTS = [
  { name: "Resume Analyst", role: "Skills & profile evidence", icon: "📄" },
  { name: "Fit Critic", role: "Requirements & gap analysis", icon: "⚖️" },
  { name: "Interview Agent", role: "Adaptive practice & depth", icon: "🎙️" },
  { name: "Career Strategist", role: "Synthesis & next action", icon: "🎯" },
];

export function JobCardInline({ job, onSelect, onAnalyzeFit }: { job: JobCardData; onSelect: (j: JobCardData) => void; onAnalyzeFit: (id: string) => void }) {
  return (
    <div className="mt-3 rounded-xl border border-white/[0.08] bg-slate-950/40 p-4 animate-fade-in-up">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-[var(--foreground)]">{job.title}</p>
          <p className="mt-0.5 text-xs text-[var(--muted)] flex items-center gap-2 flex-wrap">
            <span className="flex items-center gap-0.5"><Building2 className="h-3 w-3" /> {job.company}</span>
            <span className="flex items-center gap-0.5"><MapPin className="h-3 w-3" /> {job.location}</span>
          </p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {job.category && <span className="rounded bg-white/[0.05] px-1.5 py-0.5 text-[10px] text-[var(--muted)]">{job.category}</span>}
            {job.mode && <span className="rounded bg-cyan-500/10 px-1.5 py-0.5 text-[10px] text-cyan-200">{job.mode === "demo" ? "Demo" : "Cached demo"}</span>}
            {job.work_mode && <span className="rounded bg-white/[0.05] px-1.5 py-0.5 text-[10px] text-[var(--muted)]">{job.work_mode.replace("_", " ")}</span>}
            {job.fit_score !== null && job.fit_score !== undefined && <span className="rounded bg-indigo-500/15 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-300">{job.fit_score}/100</span>}
            {job.sponsorship && <span className="rounded bg-amber-500/10 px-1.5 py-0.5 text-[10px] text-amber-200 border border-amber-500/20">Sponsorship: {job.sponsorship}</span>}
          </div>
        </div>
        <div className="flex flex-col gap-1.5 flex-shrink-0">
          {job.salary && <span className="rounded bg-white/[0.05] px-2 py-0.5 text-[10px] text-[var(--muted)] whitespace-nowrap"><Banknote className="inline h-3 w-3 mr-0.5" />{job.salary}</span>}
          <button type="button" onClick={() => onSelect(job)} className="rounded bg-white/[0.06] px-2.5 py-1 text-[10px] text-[var(--foreground)] hover:bg-white/[0.1] transition-colors whitespace-nowrap">View role</button>
          <button type="button" onClick={() => onAnalyzeFit(job.job_id)} className="rounded bg-indigo-500/15 px-2.5 py-1 text-[10px] text-indigo-300 hover:bg-indigo-500/25 transition-colors whitespace-nowrap">Analyze fit</button>
        </div>
      </div>
    </div>
  );
}

export function OnboardingHero({ onUpload }: { onUpload: (e: ChangeEvent<HTMLInputElement>) => void }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-8 md:col-span-3">
      <div className="mx-auto max-w-2xl text-center py-8">
        <motion.span className="inline-block rounded-md bg-indigo-500/20 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-indigo-300 mb-6"
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          AI Society
        </motion.span>
        <motion.h1 className="text-3xl font-semibold tracking-tight text-[var(--foreground)] leading-tight sm:text-4xl"
          initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}>
          Let&apos;s start with you.
        </motion.h1>
        <motion.p className="mt-4 text-base leading-relaxed text-[var(--muted)] max-w-xl mx-auto"
          initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}>
          Upload your resume and your career team will build your profile.
        </motion.p>
        <motion.div className="mt-8" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.3 }}>
          <label className="cursor-pointer inline-flex items-center gap-2 rounded-xl bg-indigo-500 px-8 py-4 text-base font-semibold text-white hover:bg-indigo-400 transition-all shadow-xl shadow-indigo-500/25">
            <Upload className="h-5 w-5" />
            Upload Resume
            <input className="hidden" type="file" accept="application/pdf,.pdf" onChange={onUpload} />
          </label>
          <p className="mt-2 text-xs text-[var(--muted)]">PDF only, max 10MB. Your resume stays the evidence base for the team.</p>
        </motion.div>
      </div>
    </div>
  );
}

export function OnboardingAnalyzed({ profile, onContinue }: { profile: ResumeProfile; onContinue: () => void }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-8 md:col-span-3">
      <div className="mx-auto max-w-2xl">
        <motion.div className="text-center" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/20">
            <span className="text-2xl">✓</span>
          </div>
          <h2 className="text-2xl font-semibold text-[var(--foreground)]">Resume analyzed</h2>
          <p className="mt-2 text-sm text-[var(--muted)]">Your career team has reviewed your profile and identified your key strengths and opportunities.</p>
        </motion.div>
        <motion.div className="mt-6 rounded-lg border border-white/[0.06] bg-white/[0.02] p-4"
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}>
          <p className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)] mb-2">Profile Summary</p>
          {profile.name && <p className="text-sm text-[var(--foreground)]">{profile.name}</p>}
          {profile.skills.length > 0 && (
            <div className="mt-2">
              <p className="text-[10px] text-[var(--muted)] mb-1">Skills detected</p>
              <div className="flex flex-wrap gap-1.5">
                {profile.skills.slice(0, 8).map((skill) => (
                  <span key={skill} className="rounded bg-indigo-500/15 px-2 py-0.5 text-[10px] text-indigo-300">{skill}</span>
                ))}
              </div>
            </div>
          )}
          {profile.strengths.length > 0 && (
            <div className="mt-2"><p className="text-[10px] text-[var(--muted)] mb-1">Strengths</p><p className="text-xs text-[var(--foreground)]">{profile.strengths[0]}</p></div>
          )}
        </motion.div>
        <motion.div className="mt-6 text-center" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.4 }}>
          <button type="button" onClick={onContinue}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-500 px-8 py-4 text-base font-semibold text-white hover:bg-indigo-400 transition-all shadow-xl shadow-indigo-500/25">
            Continue to Career Team
            <ChevronRight className="h-5 w-5" />
          </button>
        </motion.div>
      </div>
    </div>
  );
}
