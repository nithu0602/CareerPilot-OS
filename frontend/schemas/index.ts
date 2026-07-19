import { z } from "zod";

export const idSchema = z.string().uuid();
export const statusSchema = z.enum(["strong", "developing", "at_risk", "active", "completed", "archived"]);
export const userSchema = z.object({ id: idSchema, fullName: z.string().min(1), email: z.string().email(), createdAt: z.string().datetime() });
export const resumeSchema = z.object({ id: idSchema, userId: idSchema, versionName: z.string().min(1), isOriginal: z.boolean(), createdAt: z.string().datetime() });
export const jobSchema = z.object({ id: idSchema, title: z.string().min(1), company: z.string().min(1), location: z.string().min(1), sponsorshipStatus: z.enum(["confirmed", "likely", "unknown", "unlikely"]) });
export const applicationSchema = z.object({ id: idSchema, jobId: idSchema, status: z.enum(["saved", "applied", "interview", "rejected", "offer"]), updatedAt: z.string().datetime() });
export const espSchema = z.object({ overall: z.number().min(0).max(100), updatedAt: z.string().datetime() });
export const recommendationSchema = z.object({ id: idSchema, evidence: z.array(z.string().min(1)).min(1), reasoning: z.string().min(1), impact: z.string().min(1), nextAction: z.string().min(1), confidence: z.number().min(0).max(1) });
export const interviewSchema = z.object({ id: idSchema, question: z.string().min(1), answer: z.string().optional(), score: z.number().min(0).max(100).optional() });
export const learningPlanSchema = z.object({ id: idSchema, goal: z.string().min(1), active: z.boolean() });
