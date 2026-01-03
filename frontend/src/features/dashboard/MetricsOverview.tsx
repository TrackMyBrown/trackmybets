import { useQuery } from "@tanstack/react-query";

import api from "@/lib/api";

export type MetricCard = {
  label: string;
  value: number | string;
  helper: string;
};

const emptyStateHint = "Upload a CSV to see sports performance.";
const emptyStateMetrics: MetricCard[] = [
  { label: "Total profit/loss", value: "—", helper: emptyStateHint },
  { label: "Win rate", value: "—", helper: emptyStateHint },
  { label: "Average stake", value: "—", helper: emptyStateHint },
  { label: "Best sport", value: "—", helper: emptyStateHint },
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

  const hasMetrics = Boolean(data && data.length > 0);
  const metrics: MetricCard[] = hasMetrics ? (data as MetricCard[]) : emptyStateMetrics;

  const formatValue = (metric: MetricCard) => {
    if (typeof metric.value !== "number") {
      return metric.value;
    }

    const label = metric.label.toLowerCase();
    const formatted = metric.value.toLocaleString(undefined, { maximumFractionDigits: 2 });

    if (label.includes("win rate")) {
      return `${formatted}%`;
    }

    if (label.includes("profit") || label.includes("p/l")) {
      return `$${formatted}`;
    }

    return formatted;
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
                ? "We couldn't load metrics just now. Upload a CSV to get started."
                : hasMetrics
                  ? "Latest metrics from your processed uploads"
                  : emptyStateHint}
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
