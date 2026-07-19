"use client";

import Link from "next/link";
import { Menu, Moon, PanelLeftClose, Sun } from "lucide-react";
import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";
import { useState, type ReactNode } from "react";
import { primaryNavigation } from "@/constants/navigation";
import { routes } from "@/constants/routes";
import { siteConfig } from "@/constants/site";
import { Avatar, Button } from "@/components/ui/primitives";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname(); const { resolvedTheme, setTheme } = useTheme(); const [open, setOpen] = useState(false); const [collapsed, setCollapsed] = useState(false);
  const page = primaryNavigation.find((item) => item.href === pathname)?.label ?? "Workspace";
  return <div className="min-h-screen bg-[var(--background)]"><header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-[var(--background)] px-4 lg:px-6"><div className="flex items-center gap-3"><Button variant="ghost" size="sm" className="lg:hidden" aria-label="Open navigation" onClick={() => setOpen(!open)}><Menu className="size-5" /></Button><p className="text-sm text-[var(--muted)]">CareerPilot OS <span className="mx-1">/</span> <span className="font-semibold text-[var(--foreground)]">{page}</span></p></div><div className="flex items-center gap-2"><Button variant="ghost" size="sm" aria-label="Toggle colour theme" onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>{resolvedTheme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}</Button><Avatar name="Demo User" /></div></header><aside className={cn("fixed inset-y-0 left-0 z-40 flex flex-col border-r bg-[var(--card)] transition-transform lg:translate-x-0", collapsed ? "w-20" : "w-64", open ? "translate-x-0" : "-translate-x-full")}><div className="flex h-16 items-center justify-between px-4"><Link href={routes.home} className="font-bold tracking-tight text-teal-700 dark:text-teal-300">{collapsed ? "CP" : siteConfig.name}</Link><Button variant="ghost" size="sm" className="hidden lg:inline-flex" aria-label="Collapse sidebar" onClick={() => setCollapsed(!collapsed)}><PanelLeftClose className="size-4" /></Button></div><nav aria-label="Primary navigation" className="flex-1 space-y-1 px-3">{primaryNavigation.map(({ href, icon: Icon, label }) => <Link key={href} href={href} onClick={() => setOpen(false)} className={cn("flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors", pathname === href ? "bg-teal-50 text-teal-800 dark:bg-teal-950 dark:text-teal-100" : "text-[var(--muted)] hover:bg-slate-100 dark:hover:bg-slate-800")}><Icon className="size-4 shrink-0" /><span className={collapsed ? "sr-only" : ""}>{label}</span></Link>)}</nav></aside><main className={cn("min-h-[calc(100vh-4rem)] transition-[padding] lg:pl-64", collapsed && "lg:pl-20")}><div className="mx-auto max-w-7xl p-5 sm:p-8">{children}</div></main></div>;
}
