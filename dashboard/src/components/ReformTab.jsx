"use client";

import { useMemo, useState } from "react";
import { colors } from "../lib/colors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import SectionHeading from "./SectionHeading";
import {
  deriveDecileBreakdown,
  deriveImpactSummary,
  getFiscalDirection,
  getPolicyMeta,
  getPolicyOptions,
  getPublishedComparison,
  getScenarioOptions,
} from "../lib/dataHelpers";
import {
  formatBn,
  formatCompactCurrency,
  formatCount,
  formatCurrency,
  formatMn,
  formatSignedBn,
  formatSignedMn,
} from "../lib/formatters";
import { getNiceTicks, getTickDomain } from "../lib/chartUtils";
import ChartLogo from "./ChartLogo";

const PALETTE = {
  border: colors.border.light,
  grid: colors.border.light,
  text: colors.gray[700],
  muted: colors.gray[500],
  gain: colors.primary[700],
  loss: colors.error,
  rentSaved: "#4CAF50",
  benefitLost: "#f44336",
  netGain: colors.primary[600],
  hb: "#2196F3",
  uc: "#FF9800",
};

const AXIS_STYLE = {
  fontSize: 12,
  fill: colors.gray[500],
};

function CustomTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-lg">
      {label !== undefined ? (
        <div className="mb-2 font-semibold text-slate-800">{label}</div>
      ) : null}
      {payload.map((entry) => (
        <div className="flex items-center justify-between gap-4" key={entry.name}>
          <span className="flex items-center gap-2 text-slate-600">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            {entry.name}
          </span>
          <span className="font-medium text-slate-800">
            {formatter ? formatter(entry.value, entry.name) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function ReformTab({ data }) {
  const policyOptions = useMemo(() => getPolicyOptions(data), [data]);
  const [selectedPolicy, setSelectedPolicy] = useState(
    policyOptions[0]?.id || "blanket_rent_reduction",
  );

  const scenarioOptions = useMemo(
    () => getScenarioOptions(data, selectedPolicy),
    [data, selectedPolicy],
  );
  const [selectedScenario, setSelectedScenario] = useState(
    scenarioOptions[0]?.id || "",
  );
  const [impactMode, setImpactMode] = useState("abs");

  // Reset scenario when policy changes
  const handlePolicyChange = (policyId) => {
    setSelectedPolicy(policyId);
    const scenarios = getScenarioOptions(data, policyId);
    setSelectedScenario(scenarios[0]?.id || "");
  };

  const summary = useMemo(
    () => deriveImpactSummary(data, selectedPolicy, selectedScenario),
    [data, selectedPolicy, selectedScenario],
  );
  const decileData = useMemo(
    () => deriveDecileBreakdown(data, selectedPolicy, selectedScenario),
    [data, selectedPolicy, selectedScenario],
  );
  const published = useMemo(
    () => getPublishedComparison(data, selectedPolicy),
    [data, selectedPolicy],
  );
  const fiscalDir = getFiscalDirection(selectedPolicy);
  const policyMeta = getPolicyMeta(selectedPolicy);

  const decileTicks = useMemo(() => {
    if (!decileData.length) return [0];
    const allValues = decileData.map((r) => r.avg_net_gain);
    return getNiceTicks([Math.min(0, ...allValues), Math.max(0, ...allValues)]);
  }, [decileData]);

  return (
    <div className="space-y-8">
      <SectionHeading
        title="Rent control policy analysis"
        description="Select a policy to see fiscal impact, distributional effects, and comparison with published estimates where available. All figures are static first-round estimates for a single year."
      />

      {/* Policy selector */}
      <div className="section-card">
        <SectionHeading
          title="Choose a policy"
          description="Five rent control policies, each with multiple scenarios."
        />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          {policyOptions.map((option) => (
            <button
              key={option.id}
              className={`selector-chip ${selectedPolicy === option.id ? "active" : ""}`}
              onClick={() => handlePolicyChange(option.id)}
            >
              <div className="text-sm font-semibold text-slate-900">
                {option.title}
              </div>
              <div className="mt-1 text-xs text-slate-500">
                {option.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Scenario selector */}
      <div className="section-card">
        <SectionHeading
          title={`${policyMeta.title} scenarios`}
          description={data.policies[selectedPolicy]?.description || ""}
        />
        <div className="flex flex-wrap gap-2">
          {scenarioOptions.map((option) => (
            <button
              key={option.id}
              className={`toggle-button ${selectedScenario === option.id ? "active" : ""}`}
              onClick={() => setSelectedScenario(option.id)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Metric cards */}
      {summary && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="metric-card">
            <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
              {fiscalDir === "cost" ? "Government cost" : "Government saving"}
            </div>
            <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              {formatSignedBn(summary.total_fiscal_bn)}
            </div>
            <div className="mt-2 text-sm text-slate-500">
              HB/UC spending change.
            </div>
          </div>
          <div className="metric-card">
            <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
              Households gaining
            </div>
            <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              {formatCount(summary.n_gaining)}
            </div>
            <div className="mt-2 text-sm text-slate-500">
              Avg gain: {formatCurrency(summary.avg_gain_per_hh)}/yr.
            </div>
          </div>
          <div className="metric-card">
            <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
              Tenant rent saved
            </div>
            <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              {formatBn(summary.rent_saved_bn)}
            </div>
            <div className="mt-2 text-sm text-slate-500">
              Total rent reduction for affected tenants.
            </div>
          </div>
          <div className="metric-card">
            <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
              Tenant net gain
            </div>
            <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              {formatSignedBn(summary.tenant_net_gain_bn)}
            </div>
            <div className="mt-2 text-sm text-slate-500">
              Rent saved minus benefit lost.
            </div>
          </div>
        </div>
      )}

      {/* Published comparison */}
      {published && published.estimates.length > 0 && (
        <div className="section-card">
          <SectionHeading
            title="Comparison with published estimates"
            description={published.description}
          />
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Metric</th>
                  <th>Published value</th>
                  <th>Year</th>
                </tr>
              </thead>
              <tbody>
                {published.estimates.map((est, i) => (
                  <tr key={i}>
                    <td className="font-medium">{est.source}</td>
                    <td>{est.metric}</td>
                    <td>{est.value}</td>
                    <td>{est.year}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Decile chart + Winners and losers — side by side */}
      {decileData.length > 0 && (
        <div className="grid gap-8 xl:grid-cols-2">
          <div className="section-card">
            <div className="flex items-start justify-between">
              <SectionHeading
                title="Average renter impact by income decile"
                description={impactMode === "abs" ? "Average annual net gain per renter household (rent saved minus benefit lost)." : "Average net gain as a share of renter household income."}
              />
              <div className="flex rounded-md border border-slate-200 text-xs font-medium overflow-hidden shrink-0 ml-4">
                <button
                  className={`px-3 py-1.5 ${impactMode === "abs" ? "bg-primary-600 text-white" : "text-slate-600 hover:bg-slate-50"}`}
                  onClick={() => setImpactMode("abs")}
                >£</button>
                <button
                  className={`px-3 py-1.5 ${impactMode === "pct" ? "bg-primary-600 text-white" : "text-slate-600 hover:bg-slate-50"}`}
                  onClick={() => setImpactMode("pct")}
                >%</button>
              </div>
            </div>
            <div className="h-[380px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={decileData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={PALETTE.grid} />
                  <XAxis
                    dataKey="decile"
                    tick={AXIS_STYLE}
                    tickLine={false}
                    label={{
                      value: "Income decile",
                      position: "insideBottom",
                      offset: -12,
                      style: AXIS_STYLE,
                    }}
                  />
                  <YAxis
                    ticks={impactMode === "abs" ? decileTicks : undefined}
                    domain={impactMode === "abs" ? getTickDomain(decileTicks) : undefined}
                    tick={AXIS_STYLE}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={impactMode === "abs" ? (v) => formatCurrency(v) : (v) => `${v}%`}
                  />
                  <ReferenceLine y={0} stroke={colors.gray[400]} strokeWidth={1} />
                  <Tooltip
                    content={
                      <CustomTooltip
                        formatter={impactMode === "abs" ? (value) => `${formatCurrency(value)}/yr` : (value) => `${Number(value).toFixed(2)}%`}
                      />
                    }
                  />
                  <Bar
                    dataKey={impactMode === "abs" ? "avg_net_gain" : "avg_net_gain_pct"}
                    name="Net gain"
                    radius={[6, 6, 0, 0]}
                  >
                    {decileData.map((row, i) => (
                      <Cell
                        key={`ng-${i}`}
                        fill={(impactMode === "abs" ? row.avg_net_gain : row.avg_net_gain_pct) >= 0 ? PALETTE.gain : PALETTE.loss}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ChartLogo />
          </div>

          <div className="section-card">
            <SectionHeading
              title="Winners and losers"
              description="Share of renters that are better off, worse off, or unaffected in each income decile."
            />
            <div className="h-[380px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={decileData} margin={{ top: 10, right: 12, left: 4, bottom: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={PALETTE.grid} />
                  <XAxis
                    dataKey="decile"
                    tick={AXIS_STYLE}
                    tickLine={false}
                    label={{
                      value: "Income decile",
                      position: "insideBottom",
                      offset: -12,
                      style: AXIS_STYLE,
                    }}
                  />
                  <YAxis
                    tick={AXIS_STYLE}
                    tickLine={false}
                    axisLine={false}
                    domain={[0, 100]}
                    tickFormatter={(v) => `${v}%`}
                  />
                  <Tooltip
                    content={
                      <CustomTooltip
                        formatter={(value) => `${Number(value).toFixed(1)}%`}
                      />
                    }
                  />
                  <Legend wrapperStyle={{ fontSize: 12, paddingTop: 4 }} iconSize={10} />
                  <Bar
                    dataKey="pct_winners"
                    name="Better off"
                    stackId="wl"
                    fill={PALETTE.gain}
                  />
                  <Bar
                    dataKey="pct_unchanged"
                    name="No change"
                    stackId="wl"
                    fill={colors.gray[300]}
                  />
                  <Bar
                    dataKey="pct_losers"
                    name="Worse off"
                    stackId="wl"
                    fill={PALETTE.loss}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ChartLogo />
          </div>
        </div>
      )}
    </div>
  );
}
