"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/app-shell";
import { Button, EmptyState } from "@/components/ui/primitives";
import { routes } from "@/constants/routes";
import { DashboardAnalysisView } from "@/features/dashboard/components/dashboard-analysis";
import { dashboardQueryKey } from "@/services/careerpilot-api";
import type { DashboardAnalysis } from "@/types";

export default function DashboardPage() {
  const { data: analysis } = useQuery({
    queryKey: dashboardQueryKey,
    queryFn: async (): Promise<DashboardAnalysis> => {
      throw new Error("A dashboard analysis must be created from a resume upload.");
    },
    enabled: false,
  });

  return (
    <AppShell>
      {analysis ? (
        <DashboardAnalysisView analysis={analysis} />
      ) : (
        <EmptyState
          title="Upload a resume to begin"
          description="Your complete career dashboard appears automatically after your resume is uploaded and analyzed."
          action={<Button asChild><Link href={routes.resume}>Upload resume</Link></Button>}
        />
      )}
    </AppShell>
  );
}
