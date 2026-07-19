import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
export function formatDate(value: string | Date) { return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value)); }
export function formatPercentage(value: number) { return new Intl.NumberFormat("en-GB", { style: "percent", maximumFractionDigits: 0 }).format(value); }
export function formatScore(value: number) { return `${Math.round(value)}/100`; }
export function sleep(milliseconds: number) { return new Promise<void>((resolve) => window.setTimeout(resolve, milliseconds)); }
export function safeParseJSON<T>(value: string, fallback: T): T { try { return JSON.parse(value) as T; } catch { return fallback; } }
export function downloadFile(contents: BlobPart, filename: string, mimeType = "text/plain") { const url = URL.createObjectURL(new Blob([contents], { type: mimeType })); const link = document.createElement("a"); link.href = url; link.download = filename; link.click(); URL.revokeObjectURL(url); }
export function debounce<T extends (...args: never[]) => void>(callback: T, wait: number) { let timer: ReturnType<typeof setTimeout> | undefined; return (...args: Parameters<T>) => { if (timer) clearTimeout(timer); timer = setTimeout(() => callback(...args), wait); }; }
export function throttle<T extends (...args: never[]) => void>(callback: T, wait: number) { let lastRun = 0; return (...args: Parameters<T>) => { const now = Date.now(); if (now - lastRun >= wait) { lastRun = now; callback(...args); } }; }
