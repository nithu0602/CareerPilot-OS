"use client";

import { useState } from "react";
import { HealthStatus } from "@/components/health-status";
import { ResumeIntelligence } from "@/components/resume-intelligence";
import { JobIntelligence } from "@/components/job-intelligence";
import { Interview } from "@/components/interview";
import { Applications } from "@/components/applications";
import { Society } from "@/components/society";
import { OverviewSummary } from "@/components/overview-summary";

const navigation = ["Overview", "Resume", "Job intelligence", "Interview", "Applications", "AI Society"] as const;
type Tab = (typeof navigation)[number];

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("Overview");

  return (
    <main className="flex min-h-screen">
      <aside className="hidden w-64 border-r border-white/10 bg-slate-950/60 p-6 md:block">
        <div className="mb-12">
          <p className="text-lg font-semibold tracking-tight">CareerPilot</p>
          <p className="mt-1 text-xs text-slate-400">Your career operating system</p>
        </div>
        <nav className="space-y-2" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              type="button"
              className={`w-full rounded-lg px-3 py-2 text-left text-sm ${activeTab === item ? "bg-indigo-500/15 text-indigo-200" : "text-slate-400 hover:text-slate-200"}`}
              key={item}
              onClick={() => setActiveTab(item)}
              aria-current={activeTab === item ? "page" : undefined}
            >
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <section className="w-full p-6 md:p-10">
        <div className="mx-auto max-w-5xl">
          <header className="mb-10">
            <p className="text-sm font-medium text-indigo-300">CareerPilot workspace</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">Build your next career move.</h1>
            <p className="mt-3 max-w-2xl text-slate-400">
              Upload your resume to understand your profile, discover suitable roles, and prepare with confidence.
            </p>
          </header>

          <nav className="mb-6 flex flex-wrap gap-2 md:hidden" aria-label="Section navigation">
            {navigation.map((item) => (
              <button
                type="button"
                key={item}
                onClick={() => setActiveTab(item)}
                className={`rounded-full px-3 py-1.5 text-xs ${activeTab === item ? "bg-indigo-500 text-white" : "bg-white/5 text-slate-400"}`}
              >
                {item}
              </button>
            ))}
          </nav>

          <div className="grid gap-4 md:grid-cols-3">
            {activeTab === "Overview" && <OverviewSummary onNavigate={setActiveTab} />}
            {activeTab === "Resume" && <ResumeIntelligence />}
            {activeTab === "Job intelligence" && <JobIntelligence />}
            {activeTab === "Interview" && <Interview />}
            {activeTab === "Applications" && <Applications />}
            {activeTab === "AI Society" && <Society />}
            {activeTab === "Overview" && <HealthStatus />}
          </div>
        </div>
      </section>
    </main>
  );
}
