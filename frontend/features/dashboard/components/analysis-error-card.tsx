"use client";

import { AlertCircle, RefreshCw } from "lucide-react";
import { Button, Card } from "@/components/ui/primitives";

export function AnalysisErrorCard({
  message,
  onRetry,
  retryDisabled,
}: {
  message: string;
  onRetry: () => void;
  retryDisabled: boolean;
}) {
  return (
    <Card role="alert" className="mx-auto max-w-2xl border-red-200 p-6 dark:border-red-900">
      <div className="flex gap-4">
        <div className="rounded-full bg-red-100 p-2 text-red-700 dark:bg-red-950 dark:text-red-300">
          <AlertCircle className="size-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="font-semibold">We couldn&apos;t analyze this resume</h2>
          <p className="mt-2 text-sm text-[var(--muted)]">{message}</p>
          <Button className="mt-5" onClick={onRetry} disabled={retryDisabled}>
            <RefreshCw className="mr-2 size-4" />
            Retry analysis
          </Button>
        </div>
      </div>
    </Card>
  );
}
