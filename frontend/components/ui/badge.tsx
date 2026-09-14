import { cn } from "@/lib/utils";

export function Badge({
  className,
  tone = "neutral",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & {
  tone?: "neutral" | "success" | "warning" | "error" | "primary";
}) {
  const toneClasses: Record<string, string> = {
    neutral: "bg-white/5 text-[var(--muted)] border-[var(--border)]",
    success: "bg-[var(--success)]/10 text-[var(--success)] border-[var(--success)]/30",
    warning: "bg-[var(--warning)]/10 text-[var(--warning)] border-[var(--warning)]/30",
    error: "bg-[var(--error)]/10 text-[var(--error)] border-[var(--error)]/30",
    primary: "bg-[var(--primary)]/15 text-[var(--accent)] border-[var(--primary)]/30",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium",
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  );
}
