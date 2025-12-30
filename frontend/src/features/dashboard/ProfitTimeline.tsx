import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import api from "@/lib/api";

type TimelinePoint = {
  date: string;
  profit: number;
  cumulative: number;
};

type ProfitTimelineProps = {
  category: "sport" | "racing";
};

function ProfitTimeline({ category }: ProfitTimelineProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["metrics", "timeseries", category],
    queryFn: async () => {
      const { data } = await api.get<TimelinePoint[]>(`/metrics/timeseries`, {
        params: { category },
      });
      return data;
    },
  });

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-slate-900">Profit & loss over time</h2>
        <p className="text-sm text-slate-600">
          {isLoading ? "Loading…" : "Track cumulative profit and individual uploads across time"}
        </p>
      </div>

      <div className="mt-6 h-64 w-full">
        {(!data || data.length === 0) && !isLoading ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            Upload a CSV to view profit trends.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data ?? []}>
              <defs>
                <linearGradient id="pnlFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#1d3ae8" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#1d3ae8" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: number) => value.toFixed(2)}
              contentStyle={{ borderRadius: 12, border: "1px solid #cbd5f5" }}
            />
              <Area
                type="monotone"
                dataKey="cumulative"
                stroke="#1d3ae8"
                fill="url(#pnlFill)"
                strokeWidth={2}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}

export default ProfitTimeline;
