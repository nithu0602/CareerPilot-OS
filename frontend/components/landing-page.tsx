"use client";

import { motion, type Variants } from "framer-motion";
import {
  ArrowRight,
  BrainCircuit,
  Briefcase,
  FileText,
  GraduationCap,
  MessageCircle,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  Upload,
  Zap,
} from "lucide-react";

const specialists = [
  { name: "Resume Analyst", role: "Understand your profile", icon: FileText, delay: 0.42 },
  { name: "Fit Critic", role: "Measure your match", icon: Target, delay: 0.54 },
  { name: "Interview Agent", role: "Practice with purpose", icon: MessageCircle, delay: 0.66 },
  { name: "Career Strategist", role: "Choose the next move", icon: BrainCircuit, delay: 0.78 },
];

const flowSteps = [
  { label: "Resume", icon: FileText, tone: "from-cyan-300 to-indigo-300" },
  { label: "Opportunities", icon: Search, tone: "from-indigo-300 to-violet-300" },
  { label: "Fit", icon: Target, tone: "from-violet-300 to-fuchsia-300" },
  { label: "Interview", icon: MessageCircle, tone: "from-fuchsia-300 to-pink-300" },
  { label: "Action", icon: Zap, tone: "from-pink-300 to-cyan-300" },
];

const container: Variants = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.09,
      delayChildren: 0.12,
    },
  },
};

const item: Variants = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] } },
};

export function LandingPage({ onEnter }: { onEnter: () => void }) {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 py-16">
      <div className="landing-bg" aria-hidden="true" />
      <div className="landing-grid" aria-hidden="true" />
      <div className="landing-scan" aria-hidden="true" />
      <div className="landing-orbit landing-orbit-one" aria-hidden="true" />
      <div className="landing-orbit landing-orbit-two" aria-hidden="true" />
      <div className="landing-particle landing-particle-one" aria-hidden="true" />
      <div className="landing-particle landing-particle-two" aria-hidden="true" />
      <div className="landing-particle landing-particle-three" aria-hidden="true" />

      <motion.div
        className="relative z-10 mx-auto flex w-full max-w-6xl flex-col items-center text-center"
        variants={container}
        initial="hidden"
        animate="show"
      >
        <motion.div variants={item} className="landing-eyebrow">
          <Sparkles className="h-3.5 w-3.5 text-cyan-300" />
          <span>Intelligent career navigation, made human</span>
          <Sparkles className="h-3.5 w-3.5 text-cyan-300" />
        </motion.div>

        <motion.h1
          variants={item}
          className="mt-7 max-w-5xl text-5xl font-bold leading-[0.95] tracking-[-0.06em] text-white sm:text-7xl lg:text-[5.5rem]"
        >
          <span className="landing-title">CAREER</span>
          <span className="landing-title-gradient">PILOT</span>
        </motion.h1>

        <motion.p
          variants={item}
          className="mt-7 text-xl font-medium tracking-tight text-indigo-100 sm:text-3xl"
        >
          Your AI career team.
        </motion.p>

        <motion.p
          variants={item}
          className="mt-4 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg sm:leading-8"
        >
          Understand your profile. Discover the right opportunities. Prepare for what&apos;s next.
        </motion.p>

        <motion.div variants={item} className="mt-10">
          <button
            type="button"
            onClick={onEnter}
            className="group relative inline-flex items-center gap-3 rounded-full bg-indigo-500 px-8 py-4 text-sm font-semibold tracking-wide text-white shadow-[0_0_45px_rgba(99,102,241,0.45)] transition-all hover:-translate-y-0.5 hover:bg-indigo-400 hover:shadow-[0_0_70px_rgba(99,102,241,0.7)] focus:outline-none focus:ring-2 focus:ring-cyan-300 focus:ring-offset-2 focus:ring-offset-slate-950 active:translate-y-0 sm:px-10 sm:py-5 sm:text-base"
          >
            <span className="absolute inset-0 rounded-full bg-white/10 opacity-0 transition-opacity group-hover:opacity-100" />
            <span className="relative inline-flex items-center gap-3">
              ENTER AI SOCIETY
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </span>
          </button>
          <p className="mt-4 text-xs tracking-wide text-slate-500">
            Start with your resume. Your team takes it from there.
          </p>
        </motion.div>

        <motion.div variants={item} className="mt-14 w-full max-w-4xl">
          <div className="mb-4 flex items-center justify-between text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
            <span>The CareerPilot pipeline</span>
            <span className="flex items-center gap-1.5 text-slate-400"><Network className="h-3 w-3" /> connected intelligence</span>
          </div>
          <div className="relative flex items-center justify-between gap-2 sm:gap-4">
            <div className="absolute left-4 right-4 top-1/2 h-px bg-gradient-to-r from-transparent via-indigo-300/40 to-transparent" />
            {flowSteps.map((step, index) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={step.label}
                  className="relative flex w-24 flex-col items-center gap-2 sm:w-32"
                  initial={{ opacity: 0, y: 14, scale: 0.94 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.55, delay: 0.7 + index * 0.1, ease: [0.22, 1, 0.36, 1] }}
                >
                  <div className={`relative z-10 flex h-10 w-10 items-center justify-center rounded-full border border-white/15 bg-slate-950/80 shadow-[0_0_25px_rgba(99,102,241,0.28)] backdrop-blur`}>
                    <Icon className={`h-4 w-4 bg-gradient-to-br ${step.tone} bg-clip-text text-transparent`} strokeWidth={1.8} />
                  </div>
                  <span className="text-[10px] font-medium tracking-wide text-slate-300 sm:text-xs">{step.label}</span>
                  {index < flowSteps.length - 1 && <span className="absolute left-[calc(100%-0.5rem)] top-4 h-px w-8 bg-indigo-300/20 sm:left-[calc(100%-0.7rem)] sm:w-12" />}
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        <motion.div variants={item} className="mt-14 grid w-full max-w-5xl grid-cols-2 gap-3 sm:grid-cols-4">
          {specialists.map((specialist) => {
            const Icon = specialist.icon;
            return (
              <motion.div
                key={specialist.name}
                whileHover={{ y: -5, borderColor: "rgba(139,92,246,0.45)" }}
                initial={{ opacity: 0, y: 22 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: specialist.delay, ease: [0.22, 1, 0.36, 1] }}
                className="group/specialist relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.035] p-4 text-left shadow-lg shadow-black/10 transition-colors hover:bg-white/[0.06]"
              >
                <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/50 to-transparent opacity-0 transition-opacity group-hover/specialist:opacity-100" />
                <div className="flex items-start justify-between">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-200 ring-1 ring-indigo-300/20">
                    <Icon className="h-4 w-4" strokeWidth={1.8} />
                  </div>
                  <span className="text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-600">0{specialists.indexOf(specialist) + 1}</span>
                </div>
                <p className="mt-4 text-sm font-semibold text-slate-100">{specialist.name}</p>
                <p className="mt-1 text-xs leading-5 text-slate-400">{specialist.role}</p>
              </motion.div>
            );
          })}
        </motion.div>

        <motion.div variants={item} className="mt-12 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[11px] text-slate-500">
          <span className="flex items-center gap-1.5"><ShieldCheck className="h-3.5 w-3.5 text-emerald-300/80" /> Evidence-led</span>
          <span className="flex items-center gap-1.5"><GraduationCap className="h-3.5 w-3.5 text-cyan-300/80" /> Graduate-ready</span>
          <span className="flex items-center gap-1.5"><Briefcase className="h-3.5 w-3.5 text-violet-300/80" /> Opportunity-focused</span>
        </motion.div>
      </motion.div>
    </main>
  );
}
