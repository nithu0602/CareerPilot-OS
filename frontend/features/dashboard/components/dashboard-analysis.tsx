"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Clock3, Lightbulb, TrendingUp } from "lucide-react";
import type { ReactNode } from "react";
import { Badge, Card, PageHeader, Progress, SectionHeader } from "@/components/ui/primitives";
import type { DashboardAnalysis } from "@/types";

const entryMotion = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 },
};

function formatSectionName(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

export function DashboardAnalysisView({ analysis }: { analysis: DashboardAnalysis }) {
  const sectionScores = Object.entries(analysis.ats.section_scores);

  return (
    <div>
      <PageHeader
        title={`${analysis.candidate_name}'s dashboard`}
        description="Your resume analysis, career opportunities, and interview preparation in one place."
        action={<Badge>Processed in {analysis.processing_time_ms} ms</Badge>}
      />

      <motion.section {...entryMotion} className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <Card className="overflow-hidden bg-gradient-to-br from-teal-700 to-teal-900 p-7 text-white dark:from-teal-800 dark:to-slate-950">
          <p className="text-sm font-semibold uppercase tracking-wide text-teal-100">ATS readiness</p>
          <div className="mt-6 flex items-end justify-between gap-4">
            <div>
              <p className="text-7xl font-bold tracking-tighter">{analysis.ats.overall_score}</p>
              <p className="mt-1 text-teal-100">out of 100</p>
            </div>
            <TrendingUp className="size-12 text-teal-200" />
          </div>
          <p className="mt-6 max-w-sm text-sm leading-6 text-teal-100">A practical view of how clearly your resume communicates the evidence recruiters and applicant tracking systems look for.</p>
        </Card>

        <Card className="p-6">
          <SectionHeader title="Section scores" description="Strength across the core parts of your resume." />
          <div className="mt-6 space-y-4">
            {sectionScores.map(([section, score]) => (
              <div key={section}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-medium">{formatSectionName(section)}</span>
                  <span className="font-semibold text-teal-700 dark:text-teal-300">{score}/100</span>
                </div>
                <Progress value={score} />
              </div>
            ))}
          </div>
        </Card>
      </motion.section>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <InsightCard title="Strengths" icon={<CheckCircle2 className="size-5 text-emerald-600" />} items={analysis.ats.strengths} />
        <InsightCard title="Areas for improvement" icon={<Lightbulb className="size-5 text-amber-600" />} items={analysis.ats.improvements} />
      </div>

      <motion.section {...entryMotion} className="mt-8">
        <SectionHeader title="Top job matches" description="Roles aligned to the evidence detected in your resume." />
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {analysis.job_matches.map((job) => (
            <Card key={job.title} className="p-5">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-semibold">{job.title}</h3>
                <Badge>{job.match}% match</Badge>
              </div>
              <p className="mt-3 text-sm font-medium text-teal-700 dark:text-teal-300">{job.salary}</p>
              <p className="mt-3 text-sm leading-6 text-[var(--muted)]">{job.reason}</p>
            </Card>
          ))}
        </div>
      </motion.section>

      <motion.section {...entryMotion} className="mt-8">
        <SectionHeader title="Interview preparation" description="Use these questions to rehearse clear, evidence-led answers." />
        <div className="mt-4 grid gap-5 xl:grid-cols-3">
          <QuestionCard title="Technical" questions={analysis.interview.technical} />
          <QuestionCard title="Behavioral" questions={analysis.interview.behavioral} />
          <QuestionCard title="Your resume" questions={analysis.interview.resume_questions} />
        </div>
      </motion.section>

      <div className="mt-8 flex items-center gap-2 text-sm text-[var(--muted)]">
        <Clock3 className="size-4" />
        <span>Processing time: {analysis.processing_time_ms} ms</span>
      </div>
    </div>
  );
}

function InsightCard({ title, icon, items }: { title: string; icon: ReactNode; items: string[] }) {
  return (
    <Card className="p-6">
      <div className="flex items-center gap-2"><span>{icon}</span><h2 className="font-semibold">{title}</h2></div>
      <ul className="mt-5 space-y-3 text-sm leading-6 text-[var(--muted)]">
        {items.map((item) => <li key={item} className="flex gap-3"><span className="mt-2 size-1.5 shrink-0 rounded-full bg-teal-600" />{item}</li>)}
      </ul>
    </Card>
  );
}

function QuestionCard({ title, questions }: { title: string; questions: string[] }) {
  return (
    <Card className="p-5">
      <h3 className="font-semibold">{title}</h3>
      <ol className="mt-4 space-y-4 text-sm leading-6 text-[var(--muted)]">
        {questions.map((question, index) => <li key={question} className="flex gap-3"><span className="font-semibold text-teal-700 dark:text-teal-300">{index + 1}.</span><span>{question}</span></li>)}
      </ol>
    </Card>
  );
}
