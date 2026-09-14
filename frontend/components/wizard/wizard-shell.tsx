import { type ReactNode } from "react";

/** Shared page shell used by every pipeline screen: same header, max-width, and padding. */
export function WizardShell({
  title,
  description,
  stepper,
  children,
}: {
  title: string;
  description: string;
  stepper: ReactNode;
  children: ReactNode;
}) {
  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-4xl">
        <header className="mb-6">
          <p className="text-sm font-medium text-[var(--accent)]">CareerPilot</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-3 max-w-2xl text-[var(--muted)]">{description}</p>
        </header>
        <div className="mb-8">{stepper}</div>
        {children}
      </div>
    </main>
  );
}
