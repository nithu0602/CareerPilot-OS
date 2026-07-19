import { AppShell } from "@/components/layout/app-shell";
import { EmptyState, PageHeader } from "@/components/ui/primitives";

export function PagePlaceholder({ title, description }: { title: string; description: string }) { return <AppShell><PageHeader title={title} description={description} /><EmptyState title={`${title} foundation ready`} description="This route is intentionally limited to the shared frontend foundation. Product workflows will be introduced in later phases." /></AppShell>; }
