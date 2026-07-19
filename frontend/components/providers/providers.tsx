"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { useState, type ReactNode } from "react";
import { createQueryClient } from "@/services/query-client";

export function Providers({ children }: { children: ReactNode }) { const [client] = useState(createQueryClient); return <NextThemesProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange><QueryClientProvider client={client}>{children}</QueryClientProvider></NextThemesProvider>; }
