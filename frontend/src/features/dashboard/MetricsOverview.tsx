import { useQuery } from "@tanstack/react-query";

import api from "@/lib/api";

export type MetricCard = {
  label: string;
  value: number | string;
  helper: string;
};

const fallbackMetrics: MetricCard[] = [
  { label: "Total profit/loss", value: -752.5, helper: "Net result since first upload" },
  { label: "Win rate", value: 0.38, helper: "Settled bets won / total" },
  { label: "Average stake", value: 47.2, helper: "Mean stake size" },
  { label: "Best sport", value: "AFL", helper: "Highest ROI" },
];

function MetricsOverview() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["metrics", "overview"],
    queryFn: async () => {
      const { data } = await api.get<MetricCard[]>("/metrics/overview");
      return data;
    },
    staleTime: 30_000,
  });

  const metrics = data ?? fallbackMetrics;

  const formatValue = (metric: MetricCard) => {
    if (typeof metric.value !== "number") {
      return metric.value;
    }

    if (metric.label.toLowerCase().includes("win rate")) {
      return `${metric.value.toLocaleString(undefined, { maximumFractionDigits: 2 })}%`;
    }

    return metric.value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  };

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Performance snapshot</h2>
          <p className="text-sm text-slate-600">
            {isLoading
              ? "Loading fresh data..."
              : isError
                ? "Showing cached placeholders"
                : "Latest metrics from your processed uploads"}
          </p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <article key={metric.label} className="rounded-2xl border border-slate-100 bg-slate-50/80 p-4 shadow-inner">
            <p className="text-sm text-slate-500">{metric.label}</p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">{formatValue(metric)}</p>
            <p className="text-xs text-slate-500">{metric.helper}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default MetricsOverview;
