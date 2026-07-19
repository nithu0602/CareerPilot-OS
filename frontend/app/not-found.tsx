import Link from "next/link";
import { Button, EmptyState } from "@/components/ui/primitives";
export default function NotFound() { return <main className="mx-auto max-w-xl p-8"><EmptyState title="Page not found" description="The page you requested is not part of this workspace." action={<Button asChild><Link href="/">Return home</Link></Button>} /></main>; }
