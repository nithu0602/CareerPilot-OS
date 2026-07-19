import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button, Card, PageHeader } from "@/components/ui/primitives";
import { routes } from "@/constants/routes";

export default function HomePage() { return <main className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center p-6"><PageHeader title="Career momentum, made clear." description="CareerPilot OS gives international graduates one calm, explainable place to direct their job search." /><Card className="mt-8 grid gap-8 p-8 md:grid-cols-[1fr_auto] md:items-end"><div><Sparkles className="mb-4 size-7 text-teal-600" /><h2 className="text-2xl font-bold">The foundation is ready.</h2><p className="mt-3 max-w-xl text-[var(--muted)]">Explore the navigation shell, shared visual system, theme support, and accessible interface states prepared for future product workflows.</p></div><Button asChild><Link href={routes.dashboard}>Enter workspace <ArrowRight className="ml-2 size-4" /></Link></Button></Card></main>; }
