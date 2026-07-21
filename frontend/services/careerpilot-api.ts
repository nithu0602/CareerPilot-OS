import type { DashboardAnalysis, ResumeUploadResponse } from "@/types";

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

export const dashboardQueryKey = ["dashboard-analysis"] as const;

export class CareerPilotApiError extends Error {
  public readonly status: number;

  public constructor(message: string, status: number) {
    super(message);
    this.name = "CareerPilotApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, init);

  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null);
    const detail = getErrorDetail(payload);
    throw new CareerPilotApiError(detail ?? "We could not complete your request.", response.status);
  }

  return (await response.json()) as T;
}

function getErrorDetail(payload: unknown): string | undefined {
  if (!payload || typeof payload !== "object" || !("detail" in payload)) {
    return undefined;
  }

  const detail = payload.detail;
  return typeof detail === "string" ? detail : undefined;
}

export async function uploadResume(file: File): Promise<ResumeUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<ResumeUploadResponse>("/api/v1/resume/upload", {
    method: "POST",
    body: formData,
  });
}

export async function analyzeDashboard(resumeText: string): Promise<DashboardAnalysis> {
  return request<DashboardAnalysis>("/api/v1/dashboard/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText }),
  });
}
