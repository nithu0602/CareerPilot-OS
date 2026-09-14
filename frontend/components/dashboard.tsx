"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ResumeIntelligence } from "@/components/resume-intelligence";
import { JobIntelligence } from "@/components/job-intelligence";
import { Interview } from "@/components/interview";
import { Applications } from "@/components/applications";
import { SocietyMain } from "@/components/society-main";

type Tab = "AI Society" | "Resume" | "Job Intelligence" | "Interview" | "Applications";

const NAVIGATION: Tab[] = ["AI Society", "Resume", "Job Intelligence", "Interview", "Applications"];

export function Dashboard({ initialTab = "AI Society", onHome }: { initialTab?: Tab; onHome?: () => void }) {
  const [activeTab, setActiveTab] = useState<Tab>(initialTab);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <main className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="hidden w-64 border-r border-white/10 bg-slate-950/60 p-6 md:block">
        <div className="mb-12">
          <button type="button" onClick={onHome} className="text-left text-lg font-semibold tracking-tight text-white hover:text-indigo-200">CareerPilot</button>
          <p className="mt-1 text-xs text-[var(--muted)]">AI career operating system</p>
          <button type="button" onClick={onHome} className="mt-2 text-xs text-slate-500 hover:text-indigo-300">CareerPilot / Home</button>
        </div>
        <nav className="space-y-2" aria-label="Main navigation">
          {NAVIGATION.map((item) => (
            <button
              type="button"
              key={item}
              className={`w-full rounded-lg px-3 py-2 text-left text-sm transition-colors ${activeTab === item ? "bg-indigo-500/15 text-indigo-200 font-medium" : "text-[var(--muted)] hover:text-[var(--foreground)]"}`}
              onClick={() => setActiveTab(item)}
              aria-current={activeTab === item ? "page" : undefined}
            >
              {item === "AI Society" ? "✦ " : ""}{item}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main area */}
      <section className="w-full p-6 md:p-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25 }}
          >
            <div className="mx-auto max-w-5xl">
              {/* Mobile nav */}
              <nav className="mb-6 flex flex-wrap gap-2 md:hidden" aria-label="Section navigation">
                <button type="button" onClick={onHome} className="rounded-full bg-white/5 px-3 py-1.5 text-xs text-[var(--muted)]">Home</button>
                {NAVIGATION.map((item) => (
                  <button
                    type="button"
                    key={item}
                    onClick={() => setActiveTab(item)}
                    className={`rounded-full px-3 py-1.5 text-xs ${activeTab === item ? "bg-indigo-500 text-white font-medium" : "bg-white/5 text-[var(--muted)]"}`}
                  >
                    {item}
                  </button>
                ))}
              </nav>

              <div className="grid gap-4 md:grid-cols-3">
                {activeTab === "AI Society" && <SocietyMain onNavigate={setActiveTab} />}
                {activeTab === "Resume" && <ResumeIntelligence onNavigate={setActiveTab} />}
                {activeTab === "Job Intelligence" && <JobIntelligence onNavigate={setActiveTab} />}
                {activeTab === "Interview" && <Interview onNavigate={setActiveTab} />}
                {activeTab === "Applications" && <Applications onNavigate={setActiveTab} />}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </section>
    </main>
  );
}
