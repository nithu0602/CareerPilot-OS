import type { Metadata } from "next";
import { Providers } from "@/components/providers/providers";
import { siteConfig } from "@/constants/site";
import "./globals.css";

export const metadata: Metadata = { title: { default: siteConfig.name, template: `%s | ${siteConfig.name}` }, description: siteConfig.description };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en" suppressHydrationWarning><body><Providers>{children}</Providers></body></html>; }
