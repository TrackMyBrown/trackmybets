import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import api from "@/lib/api";

export type BreakdownRow = {
  key: string | null;
  stake: number;
  payout: number;
  profit: number;
  roi: number;
  win_rate: number;
};

type BreakdownSectionProps = {
  category: "sport" | "racing";
  onCategoryChange?: (value: "sport" | "racing") => void;
};

const racingOptions = [
  { value: "track", label: "By track" },
  { value: "bet_type", label: "By bet type" },
  { value: "market_type", label: "By market" },
] as const;

function BreakdownSection({ category, onCategoryChange }: BreakdownSectionProps) {
  const isSport = category === "sport";

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-2xl font-semibold text-slate-900">Break it down</h3>
          <p className="text-sm text-slate-600">
            {isSport
              ? "Start with the sport, then drill into bet types and markets for that code."
              : "Drill into racing performance across tracks, bet types and markets."}
          </p>
        </div>
        <div className="flex gap-2 rounded-full bg-slate-100 p-1 text-sm">
          {(["sport", "racing"] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onCategoryChange?.(option)}
              className={`rounded-full px-3 py-1 font-semibold ${
                category === option ? "bg-white text-brand-600 shadow" : "text-slate-500"
              }`}
            >
              {option === "sport" ? "Sports" : "Racing"}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6">{isSport ? <SportsBreakdown /> : <RacingBreakdown category={category} />}</div>
    </section>
  );
}

function RacingBreakdown({ category }: { category: "sport" | "racing" }) {
  const [dimension, setDimension] = useState<(typeof racingOptions)[number]["value"]>(racingOptions[0].value);

  useEffect(() => {
    setDimension(racingOptions[0].value);
  }, [category]);

  const { data, isLoading } = useQuery({
    queryKey: ["metrics", "breakdown", category, dimension],
    queryFn: async () => {
      const { data } = await api.get<BreakdownRow[]>(`/metrics/breakdown/${dimension}`, {
        params: { category },
      });
      return data;
    },
  });

  return (
    <>
      <div className="flex gap-2 rounded-full bg-slate-100 p-1 text-sm">
        {racingOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => setDimension(option.value)}
            className={`rounded-full px-3 py-1 font-semibold ${
              option.value === dimension ? "bg-white text-brand-600 shadow" : "text-slate-500"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      <div className="mt-4 overflow-x-auto">
        <BreakdownTable rows={data ?? []} isLoading={isLoading} emptyLabel="Upload a CSV to see this breakdown." />
      </div>
    </>
  );
}

function SportsBreakdown() {
  const [selectedSport, setSelectedSport] = useState<string | null>(null);

  const { data: sports, isLoading: loadingSports } = useQuery({
    queryKey: ["metrics", "breakdown", "sport", "list"],
    queryFn: async () => {
      const { data } = await api.get<BreakdownRow[]>("/metrics/breakdown/sport", {
        params: { category: "sport" },
      });
      return data;
    },
  });

  useEffect(() => {
    if (!sports || sports.length === 0) {
      setSelectedSport(null);
      return;
    }
    const firstValid = sports.find((row) => row.key);
    if (!firstValid) {
      setSelectedSport(null);
      return;
    }
    if (!selectedSport || !sports.find((row) => row.key === selectedSport)) {
      setSelectedSport(firstValid.key as string);
    }
  }, [sports, selectedSport]);

  const sportParams = useMemo(() => ({ category: "sport", sport: selectedSport ?? undefined }), [selectedSport]);

  const { data: betTypeRows, isLoading: loadingBetTypes } = useQuery({
    enabled: Boolean(selectedSport),
    queryKey: ["metrics", "breakdown", "bet_type", selectedSport],
    queryFn: async () => {
      const { data } = await api.get<BreakdownRow[]>("/metrics/breakdown/bet_type", { params: sportParams });
      return data;
    },
  });

  const { data: marketRows, isLoading: loadingMarkets } = useQuery({
    enabled: Boolean(selectedSport),
    queryKey: ["metrics", "breakdown", "market_type", selectedSport],
    queryFn: async () => {
      const { data } = await api.get<BreakdownRow[]>("/metrics/breakdown/market_type", { params: sportParams });
      return data;
    },
  });

  return (
    <div className="grid gap-6 lg:grid-cols-[240px,1fr]">
      <div className="rounded-2xl bg-slate-50 p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Sports</p>
        <div className="mt-3 flex flex-col gap-2">
          {(sports ?? []).map((row) => {
            const isActive = row.key === selectedSport;
            const label = row.key ?? "Unclassified";
            return (
              <button
                key={label}
                type="button"
                disabled={!row.key}
                onClick={() => row.key && setSelectedSport(row.key)}
                className={`rounded-2xl border px-3 py-2 text-left disabled:opacity-50 ${
                  isActive ? "border-brand-200 bg-white shadow" : "border-transparent bg-slate-100"
                }`}
              >
                <div className="flex items-center justify-between text-sm font-semibold text-slate-900">
                  <span>{label}</span>
                  <span className={row.profit >= 0 ? "text-emerald-600" : "text-rose-600"}>
                    ${row.profit.toFixed(2)}
                  </span>
                </div>
                <p className="text-xs text-slate-500">ROI {(row.roi * 100).toFixed(1)}%</p>
              </button>
            );
          })}
          {!loadingSports && (sports ?? []).length === 0 && (
            <p className="text-sm text-slate-500">Upload a CSV to see sports performance.</p>
          )}
        </div>
      </div>

      <div className="space-y-6">
        <div className="rounded-2xl border border-slate-100 p-4">
          <h4 className="text-lg font-semibold text-slate-900">
            Bet types {selectedSport ? `for ${selectedSport}` : ""}
          </h4>
          <p className="text-sm text-slate-500">Understand where stakes are going for this sport.</p>
          <div className="mt-3 overflow-x-auto">
            <BreakdownTable
              rows={betTypeRows ?? []}
              isLoading={loadingBetTypes}
              emptyLabel="No bet types found for this sport."
            />
          </div>
        </div>

        <div className="rounded-2xl border border-slate-100 p-4">
          <h4 className="text-lg font-semibold text-slate-900">
            Markets {selectedSport ? `for ${selectedSport}` : ""}
          </h4>
          <p className="text-sm text-slate-500">See which markets are delivering returns.</p>
          <div className="mt-3 overflow-x-auto">
            <BreakdownTable
              rows={marketRows ?? []}
              isLoading={loadingMarkets}
              emptyLabel="No markets found for this sport."
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function BreakdownTable({
  rows,
  isLoading,
  emptyLabel,
}: {
  rows: BreakdownRow[];
  isLoading: boolean;
  emptyLabel: string;
}) {
  return (
    <table className="min-w-full border-separate border-spacing-y-2 text-left text-sm">
      <thead className="text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th className="px-4 py-2">Segment</th>
          <th className="px-4 py-2">Stake</th>
          <th className="px-4 py-2">Payout</th>
          <th className="px-4 py-2">Profit</th>
          <th className="px-4 py-2">ROI</th>
          <th className="px-4 py-2">Win rate</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.key ?? "unknown"} className="rounded-2xl bg-slate-50">
            <td className="px-4 py-2 font-semibold text-slate-900">{row.key ?? "Unclassified"}</td>
            <td className="px-4 py-2">{row.stake.toFixed(2)}</td>
            <td className="px-4 py-2">{row.payout.toFixed(2)}</td>
            <td className={`px-4 py-2 ${row.profit >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
              ${row.profit.toFixed(2)}
            </td>
            <td className="px-4 py-2">{(row.roi * 100).toFixed(2)}%</td>
            <td className="px-4 py-2">{(row.win_rate * 100).toFixed(2)}%</td>
          </tr>
        ))}
        {!isLoading && rows.length === 0 && (
          <tr>
            <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
              {emptyLabel}
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

export default BreakdownSection;
