"use client";
import { Button, ErrorState } from "@/components/ui/primitives";
export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) { return <main className="mx-auto max-w-xl p-8"><ErrorState title="Workspace error" description="The interface could not complete that request." /><Button className="mt-4" onClick={reset}>Try again</Button></main>; }
