"use client";

import * as ProgressPrimitive from "@radix-ui/react-progress";
import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

export function Progress({
  value,
  className,
}: {
  value: number;
  className?: string;
}) {
  return (
    <ProgressPrimitive.Root
      className={cn("h-1.5 w-full overflow-hidden rounded-full bg-white/10", className)}
      value={value}
    >
      <ProgressPrimitive.Indicator
        className="h-full rounded-full bg-[var(--primary)] transition-transform duration-700 ease-out"
        style={{ transform: `translateX(-${100 - Math.min(100, Math.max(0, value))}%)` }}
      />
    </ProgressPrimitive.Root>
  );
}

/** Radial score ring used for headline metrics such as the ATS score. */
export function ScoreRing({
  value,
  label,
  size = 160,
}: {
  value: number;
  label: string;
  size?: number;
}) {
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const target = Math.min(100, Math.max(0, value));

  // Reveal the score by animating from 0 to its target after mount, rather than
  // popping in fully formed — this is the user's first impression of the product.
  const [animated, setAnimated] = useState(0);
  useEffect(() => {
    const frame = requestAnimationFrame(() => setAnimated(target));
    return () => cancelAnimationFrame(frame);
  }, [target]);

  const offset = circumference * (1 - animated / 100);
  const tone = target >= 75 ? "var(--success)" : target >= 50 ? "var(--warning)" : "var(--error)";

  return (
    <div className="flex flex-col items-center gap-2" role="img" aria-label={`${label}: ${target} out of 100`}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={12} />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={tone}
            strokeWidth={12}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 1.1s cubic-bezier(0.22, 1, 0.36, 1)" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-semibold tabular-nums">{animated}</span>
          <span className="text-xs text-[var(--muted)]">/ 100</span>
        </div>
      </div>
      <p className="text-sm font-medium text-[var(--muted)]">{label}</p>
    </div>
  );
}
