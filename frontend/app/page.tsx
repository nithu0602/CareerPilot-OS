"use client";

import { useState } from "react";
import { LandingPage } from "@/components/landing-page";
import { Dashboard } from "@/components/dashboard";

export default function Home() {
  const [entered, setEntered] = useState(false);
  const [initialTab, setInitialTab] = useState<"Resume" | "AI Society" | "Job Intelligence" | "Interview" | "Applications">("AI Society");

  if (!entered) {
    return <LandingPage onEnter={() => { setInitialTab("Resume"); setEntered(true); }} />;
  }

  return <Dashboard initialTab={initialTab} onHome={() => setEntered(false)} />;
}
