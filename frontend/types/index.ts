export type ID = string;
export type Timestamp = string;
export type Status = "strong" | "developing" | "at_risk" | "active" | "completed" | "archived";
export interface User { id: ID; fullName: string; email: string; createdAt: Timestamp; }
export interface Resume { id: ID; userId: ID; versionName: string; isOriginal: boolean; createdAt: Timestamp; }
export interface Job { id: ID; title: string; company: string; location: string; sponsorshipStatus: "confirmed" | "likely" | "unknown" | "unlikely"; }
export interface Application { id: ID; jobId: ID; status: "saved" | "applied" | "interview" | "rejected" | "offer"; updatedAt: Timestamp; }
export interface Agent { name: "resume" | "job" | "strategy" | "interview" | "learning" | "application"; status: "idle" | "running" | "complete" | "failed"; }
export interface ESPScore { overall: number; updatedAt: Timestamp; }
export interface Recommendation { id: ID; evidence: string[]; reasoning: string; impact: string; nextAction: string; confidence: number; }
export interface Interview { id: ID; question: string; answer?: string; score?: number; }
export interface LearningPlan { id: ID; goal: string; active: boolean; }
export interface APIResponse<T> { data: T; meta: Record<string, unknown>; }
export interface APIError { error: { code: string; message: string; details?: Record<string, unknown>; }; }
export interface PaginatedResponse<T> extends APIResponse<T[]> { meta: { page: number; pageSize: number; total: number; }; }
export interface ResumeUploadResponse { filename: string; file_type: "pdf" | "docx"; file_size_bytes: number; page_count: number | null; character_count: number; word_count: number; raw_text: string; }
export interface ATSSectionScores { skills: number; experience: number; education: number; projects: number; keywords: number; }
export interface ATSAnalysis { overall_score: number; section_scores: ATSSectionScores; strengths: string[]; improvements: string[]; }
export interface JobMatch { title: string; match: number; salary: string; reason: string; }
export interface InterviewPreparation { technical: string[]; behavioral: string[]; resume_questions: string[]; }
export interface DashboardAnalysis { candidate_name: string; ats: ATSAnalysis; job_matches: JobMatch[]; interview: InterviewPreparation; processing_time_ms: number; }
