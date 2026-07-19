from pathlib import Path
from textwrap import dedent

root = Path.cwd()
frontend = root / 'frontend'

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).strip() + '\n', encoding='utf-8')

files = {
    root / '.gitignore': '''
node_modules/
frontend/.next/
frontend/out/
frontend/coverage/
frontend/playwright-report/
frontend/test-results/
.env
.env.local
frontend/.env
frontend/.env.local
*.log
''',
    root / '.prettierrc.json': '''
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100
}
''',
    root / '.prettierignore': '''
node_modules
.next
coverage
dist
''',
    root / '.env.example': '''
OPENAI_API_KEY=replace-me
NEXT_PUBLIC_SUPABASE_URL=https://example.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=replace-me
SUPABASE_SERVICE_ROLE_KEY=replace-me
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/careerpilot
''',
    root / 'LICENSE': '''
MIT License

Copyright (c) 2026 CareerPilot OS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''',
    frontend / 'package.json': '''
{
  "name": "careerpilot-os",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "@hookform/resolvers": "^3.10.0",
    "@supabase/supabase-js": "^2.49.5",
    "@tanstack/react-query": "^5.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "drizzle-orm": "^0.36.0",
    "framer-motion": "^11.11.0",
    "lucide-react": "^0.468.0",
    "next": "15.3.3",
    "openai": "^5.0.0",
    "react": "19.1.0",
    "react-dom": "19.1.0",
    "react-hook-form": "^7.25.0",
    "tailwind-merge": "^2.4.0",
    "zod": "^3.24.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.50.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.2.0",
    "@types/node": "^22.10.0",
    "@types/react": "^19.1.0",
    "@types/react-dom": "^19.1.0",
    "autoprefixer": "^10.4.20",
    "drizzle-kit": "^0.30.0",
    "eslint": "^9.14.0",
    "eslint-config-next": "^15.3.3",
    "husky": "^9.1.0",
    "jsdom": "^25.0.0",
    "lint-staged": "^15.2.0",
    "postcss": "^8.4.49",
    "prettier": "^3.5.0",
    "tailwindcss": "^4.1.0",
    "typescript": "^5.7.3",
    "vitest": "^2.1.0"
  }
}
''',
    frontend / 'tsconfig.json': '''
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "es2022"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    },
    "plugins": [{ "name": "next" }]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
''',
    frontend / 'next-env.d.ts': '''
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
''',
    frontend / 'next.config.ts': '''
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
};

export default nextConfig;
''',
    frontend / 'postcss.config.mjs': '''
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
''',
    frontend / '.eslintrc.json': '''
{
  "extends": ["next/core-web-vitals", "prettier"]
}
''',
    frontend / 'tailwind.config.ts': '''
import type { Config } from 'tailwindcss';

export default {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
    },
  },
  plugins: [],
} satisfies Config;
''',
    frontend / 'drizzle.config.ts': '''
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './db/schema/**/*.ts',
  out: './db/migrations',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL ?? '',
  },
});
''',
    frontend / 'middleware.ts': '''
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  return NextResponse.next();
}
''',
    frontend / 'app/layout.tsx': '''
import type { Metadata } from 'next';
import './globals.css';
import { AppShell } from '@/components/layout/app-shell';
import { ThemeProvider } from '@/components/ui/theme-toggle';

export const metadata: Metadata = {
  title: 'CareerPilot OS',
  description: 'Engineering foundation for an AI-native career platform.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <AppShell>{children}</AppShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
''',
    frontend / 'app/page.tsx': '''
import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/dashboard');
}
''',
    frontend / 'app/loading.tsx': '''
import { LoadingSpinner } from '@/components/ui/loading-spinner';

export default function Loading() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <LoadingSpinner label="Loading" />
    </div>
  );
}
''',
    frontend / 'app/error.tsx': '''
'use client';

import { Button } from '@/components/ui/button';

export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
      <p className="text-lg font-medium">Something went wrong.</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
''',
    frontend / 'app/dashboard/page.tsx': '''
import { PageContainer } from '@/components/common/page-container';
import { SectionHeader } from '@/components/common/section-header';
import { StatCard } from '@/components/common/stat-card';

export default function DashboardPage() {
  return (
    <PageContainer>
      <SectionHeader title="Dashboard" description="A foundational shell for the future product experience." />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="System Health" value="Stable" />
        <StatCard label="Agents" value="0" />
        <StatCard label="Models" value="Planned" />
      </div>
    </PageContainer>
  );
}
''',
    frontend / 'app/resume/page.tsx': '''
import { PageContainer } from '@/components/common/page-container';
import { SectionHeader } from '@/components/common/section-header';

export default function ResumePage() {
  return (
    <PageContainer>
      <SectionHeader title="Resume" description="Coming Soon" />
      <p className="text-sm text-muted-foreground">No business logic is implemented in this milestone.</p>
    </PageContainer>
  );
}
''',
    frontend / 'app/jobs/page.tsx': '''
import { PageContainer } from '@/components/common/page-container';
import { SectionHeader } from '@/components/common/section-header';

export default function JobsPage() {
  return (
    <PageContainer>
      <SectionHeader title="Jobs" description="Coming Soon" />
    </PageContainer>
  );
}
''',
    frontend / 'app/applications/page.tsx': '''
import { PageContainer } from '@/components/common/page-container';
import { SectionHeader } from '@/components/common/section-header';

export default function ApplicationsPage() {
  return (
    <PageContainer>
      <SectionHeader title="Applications" description="Coming Soon" />
    </PageContainer>
  );
}
''',
    frontend / 'app/interview/page.tsx': '''
import { PageContainer } from '@/components/common/page-container';
import { SectionHeader } from '@/components/common/section-header';

export default function InterviewPage() {
  return (
    <PageContainer>
      <SectionHeader title="Interview" description="Coming Soon" />
    </PageContainer>
  );
}
''',
    frontend / 'app/learning/page.tsx': '''
import { PageContainer } from '@/components/common/page-container';
import { SectionHeader } from '@/components/common/section-header';

export default function LearningPage() {
  return (
    <PageContainer>
      <SectionHeader title="Learning" description="Coming Soon" />
    </PageContainer>
  );
}
''',
    frontend / 'app/settings/page.tsx': '''
import { PageContainer } from '@/components/common/page-container';
import { SectionHeader } from '@/components/common/section-header';

export default function SettingsPage() {
  return (
    <PageContainer>
      <SectionHeader title="Settings" description="Coming Soon" />
    </PageContainer>
  );
}
''',
    frontend / 'components/layout/app-shell.tsx': '''
'use client';

import { motion } from 'framer-motion';
import { Sidebar } from './sidebar';
import { Header } from './header';
import { Footer } from './footer';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <div className="flex flex-1">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Header />
          <motion.main initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex-1 p-6">
            {children}
          </motion.main>
          <Footer />
        </div>
      </div>
    </div>
  );
}
''',
    frontend / 'components/layout/sidebar.tsx': '''
import Link from 'next/link';
import { LayoutDashboard, FileText, Briefcase, ClipboardList, MessagesSquare, BookOpen, Settings } from 'lucide-react';

const items = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/resume', label: 'Resume', icon: FileText },
  { href: '/jobs', label: 'Jobs', icon: Briefcase },
  { href: '/applications', label: 'Applications', icon: ClipboardList },
  { href: '/interview', label: 'Interview', icon: MessagesSquare },
  { href: '/learning', label: 'Learning', icon: BookOpen },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="hidden w-72 border-r bg-muted/30 p-6 lg:block">
      <div className="mb-8">
        <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">CareerPilot OS</p>
        <h2 className="mt-2 text-xl font-semibold">Engineering Foundation</h2>
      </div>
      <nav className="space-y-2">
        {items.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href} className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition hover:bg-accent">
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
''',
    frontend / 'components/layout/header.tsx': '''
import { ThemeToggle } from '@/components/ui/theme-toggle';

export function Header() {
  return (
    <header className="flex items-center justify-between border-b px-6 py-4">
      <div>
        <p className="text-sm font-medium">Milestone 1</p>
        <p className="text-sm text-muted-foreground">Project foundation and engineering setup</p>
      </div>
      <ThemeToggle />
    </header>
  );
}
''',
    frontend / 'components/layout/footer.tsx': '''
export function Footer() {
  return (
    <footer className="border-t px-6 py-4 text-sm text-muted-foreground">
      Foundation scaffolding only. No product features implemented.
    </footer>
  );
}
''',
    frontend / 'components/common/page-container.tsx': '''
export function PageContainer({ children }: { children: React.ReactNode }) {
  return <div className="mx-auto flex max-w-6xl flex-col gap-6">{children}</div>;
}
''',
    frontend / 'components/common/section-header.tsx': '''
export function SectionHeader({ title, description }: { title: string; description: string }) {
  return (
    <div className="space-y-1">
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
''',
    frontend / 'components/common/stat-card.tsx': '''
import { Card } from '@/components/ui/card';

export function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-6">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </Card>
  );
}
''',
    frontend / 'components/ui/button.tsx': '''
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:opacity-90',
        outline: 'border border-input bg-background hover:bg-accent',
        ghost: 'hover:bg-accent',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 px-3',
        lg: 'h-11 px-6',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
);

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant, size, className }))} {...props} />;
}
''',
    frontend / 'components/ui/card.tsx': '''
import { cn } from '@/lib/utils';

export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn('rounded-xl border bg-card p-6 shadow-sm', className)}>{children}</div>;
}
''',
    frontend / 'components/ui/badge.tsx': '''
import { cn } from '@/lib/utils';

export function Badge({ className, children }: { className?: string; children: React.ReactNode }) {
  return <span className={cn('inline-flex rounded-full border px-2.5 py-0.5 text-xs', className)}>{children}</span>;
}
''',
    frontend / 'components/ui/input.tsx': '''
import { cn } from '@/lib/utils';

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn('flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm', className)} {...props} />;
}
''',
    frontend / 'components/ui/textarea.tsx': '''
import { cn } from '@/lib/utils';

export function Textarea({ className, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn('flex min-h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm', className)} {...props} />;
}
''',
    frontend / 'components/ui/skeleton.tsx': '''
export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-muted ${className}`} />;
}
''',
    frontend / 'components/ui/loading-spinner.tsx': '''
export function LoadingSpinner({ label = 'Loading' }: { label?: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      <span className="text-sm text-muted-foreground">{label}</span>
    </div>
  );
}
''',
    frontend / 'components/ui/progress-bar.tsx': '''
export function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
      <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${value}%` }} />
    </div>
  );
}
''',
    frontend / 'components/ui/dialog.tsx': '''
export function Dialog({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-background p-6 shadow-sm">
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="mt-4">{children}</div>
    </div>
  );
}
''',
    frontend / 'components/ui/theme-toggle.tsx': '''
'use client';

import { Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Button } from './button';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('theme') as 'light' | 'dark' | null;
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const resolved = storedTheme ?? systemTheme;
    setTheme(resolved);
    document.documentElement.classList.toggle('dark', resolved === 'dark');
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    window.localStorage.setItem('theme', theme);
  }, [theme]);

  return <div>{children}</div>;
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (storedTheme) {
      setTheme(storedTheme);
    }
  }, []);

  return (
    <Button variant="outline" size="sm" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </Button>
  );
}
''',
    frontend / 'lib/utils.ts': '''
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
''',
    frontend / 'lib/env.ts': '''
import { z } from 'zod';

const envSchema = z.object({
  OPENAI_API_KEY: z.string().min(1).optional(),
  NEXT_PUBLIC_SUPABASE_URL: z.string().url().optional(),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1).optional(),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1).optional(),
  DATABASE_URL: z.string().min(1).optional(),
});

export const env = envSchema.parse({
  OPENAI_API_KEY: process.env.OPENAI_API_KEY,
  NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
  NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY,
  DATABASE_URL: process.env.DATABASE_URL,
});
''',
    frontend / 'lib/logger.ts': '''
export function createLogger(scope: string) {
  return {
    info: (message: string, meta?: Record<string, unknown>) => console.info(`[${scope}] ${message}`, meta ?? {}),
    error: (message: string, meta?: Record<string, unknown>) => console.error(`[${scope}] ${message}`, meta ?? {}),
  };
}
''',
    frontend / 'lib/api.ts': '''
export type ApiResponse<T> = {
  data: T | null;
  error: string | null;
};

export function createApiResponse<T>(data: T | null, error: string | null = null): ApiResponse<T> {
  return { data, error };
}
''',
    frontend / 'lib/result.ts': '''
export type Result<T, E = Error> = {
  ok: true;
  value: T;
} | {
  ok: false;
  error: E;
};
''',
    frontend / 'lib/date.ts': '''
export function formatDate(value: Date | string) {
  return new Date(value).toISOString().slice(0, 10);
}
''',
    frontend / 'lib/constants.ts': '''
export const NAV_ITEMS = ['Dashboard', 'Resume', 'Jobs', 'Applications', 'Interview', 'Learning', 'Settings'] as const;
export const APP_NAME = 'CareerPilot OS';
''',
    frontend / 'types/domain.ts': '''
export interface Resume {
  id: string;
  userId: string;
  title?: string;
  summary?: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location?: string;
}

export interface Application {
  id: string;
  jobId: string;
  userId: string;
  status: 'draft' | 'submitted' | 'interview' | 'offer' | 'closed';
}

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface ESP {
  id: string;
  name: string;
  description?: string;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
}

export interface Recommendation {
  id: string;
  score: number;
  rationale?: string;
}

export interface CoordinatorState {
  status: 'idle' | 'running' | 'complete' | 'error';
  steps: string[];
}
''',
    frontend / 'schemas/domain.ts': '''
import { z } from 'zod';

export const resumeSchema = z.object({
  id: z.string().uuid().optional(),
  userId: z.string().uuid(),
  title: z.string().optional(),
  summary: z.string().optional(),
});

export const jobSchema = z.object({
  id: z.string().uuid().optional(),
  title: z.string().min(1),
  company: z.string().min(1),
  location: z.string().optional(),
});

export const espSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string().min(1),
  description: z.string().optional(),
});

export const recommendationSchema = z.object({
  id: z.string().uuid().optional(),
  score: z.number().min(0).max(100),
  rationale: z.string().optional(),
});

export const agentResultSchema = z.object({
  agentId: z.string(),
  status: z.enum(['success', 'error']),
  output: z.string().optional(),
});

export const coordinatorResultSchema = z.object({
  status: z.enum(['complete', 'error']),
  steps: z.array(z.string()),
});
''',
    frontend / 'config/site.ts': '''
export const siteConfig = {
  name: 'CareerPilot OS',
  description: 'Engineering foundation for an AI-native career platform.',
  navItems: ['Dashboard', 'Resume', 'Jobs', 'Applications', 'Interview', 'Learning', 'Settings'],
};
''',
    frontend / 'styles/globals.css': '''
@import 'tailwindcss';

:root {
  --background: 0 0% 100%;
  --foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --accent: 210 40% 96.1%;
  --card: 0 0% 100%;
  --input: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --border: 217.2 32.6% 17.5%;
  --accent: 217.2 32.6% 17.5%;
  --card: 222.2 84% 4.9%;
  --input: 217.2 32.6% 17.5%;
  --ring: 224.3 76.3% 48%;
}

body {
  margin: 0;
  min-height: 100vh;
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
}

* {
  box-sizing: border-box;
}
''',
    frontend / 'db/schema/index.ts': '''
export const schema = {};
''',
    frontend / 'tests/setup.ts': '''
import '@testing-library/jest-dom/vitest';
''',
    frontend / 'vitest.config.ts': '''
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});
''',
    frontend / 'playwright.config.ts': '''
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://127.0.0.1:3000',
  },
});
''',
    frontend / 'tests/app-shell.test.tsx': '''
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { SectionHeader } from '@/components/common/section-header';

describe('SectionHeader', () => {
  it('renders the title and description', () => {
    render(<SectionHeader title="Resume" description="Coming Soon" />);
    expect(screen.getByText('Resume')).toBeInTheDocument();
    expect(screen.getByText('Coming Soon')).toBeInTheDocument();
  });
});
''',
    frontend / 'tests/e2e/smoke.spec.ts': '''
import { test, expect } from '@playwright/test';

test('homepage redirects to dashboard', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/dashboard/);
});
''',
    frontend / 'README.md': '''
# CareerPilot OS Frontend

This package contains the engineering foundation for CareerPilot OS.

## Scripts

- npm run dev
- npm run lint
- npm run typecheck
- npm run test
- npm run build
''',
    frontend / 'public/.gitkeep': ''
}

for path, content in files.items():
    write(path, content)

print(f'Created {len(files)} files under {frontend}')