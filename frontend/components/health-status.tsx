"use client";

import { useEffect, useState } from "react";

type HealthState = "checking" | "connected" | "offline";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function HealthStatus() {
  const [status, setStatus] = useState<HealthState>("checking");

  useEffect(() => {
    fetch(`${apiUrl}/api/health`)
      .then((response) => {
        if (!response.ok) throw new Error("Health request failed");
        setStatus("connected");
      })
      .catch(() => setStatus("offline"));
  }, []);

  const label = status === "checking" ? "Checking backend..." : status === "connected" ? "Backend connected" : "Backend offline";
  const color = status === "connected" ? "bg-emerald-400" : status === "offline" ? "bg-rose-400" : "bg-amber-400";

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">
      <p className="text-sm text-slate-400">System status</p>
      <div className="mt-5 flex items-center gap-3">
        <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
        <span className="text-sm">{label}</span>
      </div>
      <p className="mt-4 text-xs leading-5 text-slate-500">The dashboard checks the FastAPI health endpoint on load.</p>
    </div>
  );
}
