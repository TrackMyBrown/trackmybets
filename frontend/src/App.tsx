import { useState } from "react";

import UploadPanel from "@/features/upload/UploadPanel";
import MetricsOverview from "@/features/dashboard/MetricsOverview";
import BreakdownSection from "@/features/dashboard/BreakdownSection";
import ProfitTimeline from "@/features/dashboard/ProfitTimeline";
import CashSummary from "@/features/dashboard/CashSummary";

function App() {
  const [category, setCategory] = useState<"sport" | "racing">("sport");

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-4 py-12 sm:px-8">
      <header className="rounded-3xl bg-white/80 p-8 shadow-card backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brand-600">TrackMyBets 2.0</p>
        <h1 className="mt-3 text-4xl font-semibold leading-snug text-slate-900">
          Understand your betting performance with clarity
        </h1>
        <p className="mt-4 max-w-3xl text-base text-slate-600">
          Upload your Sportsbet history once, then explore how racing and sports bets contribute to long-term profit or
          loss. Everything stays local during the MVP phase.
        </p>
      </header>

      <main className="flex flex-col gap-10 pb-16">
        <section>
          <UploadPanel />
        </section>

        <section className="flex flex-col gap-6">
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">Insights</h2>
            <p className="text-sm text-slate-600">Explore trends, timelines, and breakdowns for your betting history.</p>
          </div>

          <CashSummary />
          <MetricsOverview />
          <ProfitTimeline category={category} />
          <BreakdownSection category={category} onCategoryChange={setCategory} />
        </section>
      </main>
    </div>
  );
}

export default App;
