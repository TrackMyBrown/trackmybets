import { useQuery } from "@tanstack/react-query";

import api from "@/lib/api";

type CashflowResponse = {
  deposits: number;
  withdrawals: number;
};

function CashSummary() {
  const { data, isLoading } = useQuery({
    queryKey: ["metrics", "cashflow"],
    queryFn: async () => {
      const { data } = await api.get<CashflowResponse>("/metrics/cashflow");
      return data;
    },
  });

  const deposits = data?.deposits ?? 0;
  const withdrawals = data?.withdrawals ?? 0;
  const net = deposits - withdrawals;
  const netDisplay = net > 0 ? -net : net;
  const netTone = net > 0 ? "negative" : "positive";

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <CashCard label="Total deposits" value={deposits} tone="positive" loading={isLoading} />
      <CashCard label="Total withdrawals" value={withdrawals} tone="negative" loading={isLoading} />
      <CashCard
        label="Net cash flow"
        value={netDisplay}
        tone={netTone}
        loading={isLoading}
        helper="Does not include current balance."
      />
    </div>
  );
}

type CashCardProps = {
  label: string;
  value: number;
  tone: "positive" | "negative";
  loading: boolean;
  helper?: string;
};

function CashCard({ label, value, tone, loading, helper }: CashCardProps) {
  const formatted = loading ? "—" : `$${value.toFixed(2)}`;
  const isPositive = tone === "positive";
  const color = isPositive ? "text-emerald-600" : "text-rose-600";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${color}`}>{formatted}</p>
      {helper && <p className="mt-1 text-xs text-slate-500">{helper}</p>}
    </div>
  );
}

export default CashSummary;
