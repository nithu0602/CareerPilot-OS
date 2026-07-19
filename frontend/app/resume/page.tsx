import { ResumeUploader } from "@/features/resume/components/ResumeUploader";

export default function ResumePage() {
  return (
    <main className="mx-auto max-w-5xl p-8">
      <div className="mb-10">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-400">
          CareerPilot OS
        </p>

        <h1 className="mt-2 text-5xl font-bold text-white">
          Resume
        </h1>

        <p className="mt-4 max-w-2xl text-slate-400">
          Upload and manage your resumes. This is the starting point for
          AI-powered resume analysis, job matching, and career insights.
        </p>
      </div>

      <ResumeUploader />
    </main>
  );
}