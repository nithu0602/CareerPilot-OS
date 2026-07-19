import { BriefcaseBusiness, BrainCircuit, FileText, LayoutDashboard, Settings, Sparkles, Target } from "lucide-react";
import { routes } from "@/constants/routes";

export const primaryNavigation = [
  { label: "Dashboard", href: routes.dashboard, icon: LayoutDashboard },
  { label: "Resume", href: routes.resume, icon: FileText },
  { label: "Jobs", href: routes.jobs, icon: BriefcaseBusiness },
  { label: "Applications", href: routes.applications, icon: Target },
  { label: "Interview", href: routes.interview, icon: BrainCircuit },
  { label: "Strategy", href: routes.strategy, icon: Sparkles },
  { label: "Settings", href: routes.settings, icon: Settings },
] as const;
