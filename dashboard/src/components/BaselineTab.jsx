"use client";

import { useMemo, useState } from "react";
import { colors } from "../lib/colors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import SectionHeading from "./SectionHeading";
import { formatBn, formatCount, formatCurrency, formatPct } from "../lib/formatters";

import ChartLogo from "./ChartLogo";

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
            {formatter ? formatter(entry.value) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

function InfoTooltip({ text }) {
  const [show, setShow] = useState(false);
  return (
    <span className="relative inline-block ml-1.5">
      <button
        className="inline-flex h-4 w-4 items-center justify-center rounded-full border border-slate-300 text-[10px] font-bold text-slate-400 hover:border-slate-400 hover:text-slate-600"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={() => setShow((s) => !s)}
      >
        i
      </button>
      {show && (
        <div className="absolute bottom-full left-1/2 z-50 mb-2 w-72 -translate-x-1/2 rounded-lg border border-slate-200 bg-white p-3 text-xs text-slate-600 shadow-lg">
          {text}
        </div>
      )}
    </span>
  );
}

function BenefitToggle({ mode, setMode }) {
  return (
    <div className="flex rounded-md border border-slate-200 text-xs font-medium overflow-hidden shrink-0 ml-4">
      <button
        className={`px-3 py-1.5 ${mode === "hb" ? "bg-primary-600 text-white" : "text-slate-600 hover:bg-slate-50"}`}
        onClick={() => setMode("hb")}
      >HB</button>
      <button
        className={`px-3 py-1.5 ${mode === "uc" ? "bg-primary-600 text-white" : "text-slate-600 hover:bg-slate-50"}`}
        onClick={() => setMode("uc")}
      >UC</button>
    </div>
  );
}

export default function BaselineTab({ data }) {
  const baseline = data.baseline;
  const summary = baseline.summary;
  const byTenure = baseline.by_tenure;
  const byDecile = baseline.by_decile;
  const byRegion = baseline.by_region || [];
  const byHhType = baseline.by_hh_type || [];
  const tenureDist = baseline.tenure_distribution || [];
  const distImpact = baseline.distributional_impact || { hb: [], uc_housing: [] };
  const [rentBurdenMode, setRentBurdenMode] = useState("pct");
  const [benefitMode, setBenefitMode] = useState("uc");

  const sortedTenureDist = useMemo(() => {
    return [...tenureDist].sort((a, b) => b.pct - a.pct);
  }, [tenureDist]);

  const sortedRegions = useMemo(() => {
    return [...byRegion].sort((a, b) => b.avg_rent - a.avg_rent);
  }, [byRegion]);

  const benefitLabel = benefitMode === "hb" ? "Housing Benefit" : "UC housing element";

  return (
    <div className="space-y-10">

      {/* Summary metrics — above everything */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            Renters
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            {formatCount(summary.n_private_renters + summary.n_social_renters)}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            {formatCount(summary.n_private_renters)} private, {formatCount(summary.n_social_renters)} social
          </div>
        </div>
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            Total rent
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            {formatBn(summary.total_private_rent_bn + summary.total_social_rent_bn)}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            Private {formatBn(summary.total_private_rent_bn)}, social {formatBn(summary.total_social_rent_bn)}
          </div>
        </div>
        <div className="metric-card">
          <div className="text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            HB + UC housing spending
          </div>
          <div className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            {formatBn(summary.total_housing_benefit_bn)}
          </div>
          <div className="mt-1 text-sm text-slate-500">
            HB {formatBn(summary.hb_spending_bn)} + UC {formatBn(summary.uc_housing_spending_bn)}
          </div>
        </div>
      </div>

      {/* ================================================================ */}
      {/* SECTION 1: RENTS & TENURE                                       */}
      {/* ================================================================ */}
      <SectionHeading
        title="Rents and tenure"
        description="This section shows rent levels, tenure distribution, and affordability across the UK. All figures are per household per year from FRS microdata projected to 2026."
      />

      {/* Row 1: Rent by tenure table + Tenure distribution chart */}
      <div className="grid gap-8 xl:grid-cols-2">
        <div className="section-card">
          <div className="flex items-center">
            <SectionHeading
              title="Rent by tenure"
              description="Average annual rent per household by tenure type."
            />
            <InfoTooltip text="Mean annual rent per household from FRS microdata projected to 2026. Our figures are higher than published medians (EHS 2023-24: council ~£5k, HA ~£6k, private ~£11k) for three reasons: (1) we report means not medians — high-rent outliers pull means up; (2) FRS data is uprated to 2026 prices; (3) EHS covers England only. Rent-to-income ratios (20-26%) are lower than EHS (~28-33%) because we use gross household income rather than net." />
          </div>
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Tenure</th>
                  <th>Avg rent</th>
                  <th>Avg income</th>
                  <th>Rent/income</th>
                </tr>
              </thead>
              <tbody>
                {byTenure.map((row) => (
                  <tr key={row.tenure}>
                    <td className="font-medium">{row.tenure}</td>
                    <td>{formatCurrency(row.avg_rent)}</td>
                    <td>{row.avg_income ? formatCurrency(row.avg_income) : "—"}</td>
                    <td>{row.rent_to_income_pct > 0 ? formatPct(row.rent_to_income_pct) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {tenureDist.length > 0 && (
          <div className="section-card">
            <SectionHeading
              title="Tenure distribution"
              description="Share of UK households by tenure type."
            />
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sortedTenureDist} layout="vertical" margin={{ left: 10, right: 30, top: 10, bottom: 10 }} barSize={28}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} horizontal={false} />
                  <XAxis
                    type="number"
                    tick={AXIS_STYLE}
                    tickLine={false}
                    tickFormatter={(v) => `${v}%`}
                  />
                  <YAxis
                    type="category"
                    dataKey="tenure"
                    tick={{ ...AXIS_STYLE, fontSize: 13 }}
                    tickLine={false}
                    axisLine={false}
                    width={160}
                  />
                  <Tooltip content={<CustomTooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />} />
                  <Bar dataKey="pct" name="Share of households" fill={colors.primary[600]} radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ChartLogo />
          </div>
        )}
      </div>

      {/* Row 2: Rent burden by decile + Average rent by household type */}
      <div className="grid gap-8 xl:grid-cols-2">
        <div className="section-card">
          <div className="flex items-start justify-between">
            <SectionHeading
              title={`Rent burden by decile${rentBurdenMode === "pct" ? " (% of income)" : ""}`}
              description={rentBurdenMode === "pct" ? "Average rent as a share of household income by decile." : "Average annual rent per household by income decile."}
            />
            <div className="flex rounded-md border border-slate-200 text-xs font-medium overflow-hidden shrink-0 ml-4">
              <button
                className={`px-3 py-1.5 ${rentBurdenMode === "pct" ? "bg-primary-600 text-white" : "text-slate-600 hover:bg-slate-50"}`}
                onClick={() => setRentBurdenMode("pct")}
              >%</button>
              <button
                className={`px-3 py-1.5 ${rentBurdenMode === "amount" ? "bg-primary-600 text-white" : "text-slate-600 hover:bg-slate-50"}`}
                onClick={() => setRentBurdenMode("amount")}
              >£</button>
            </div>
          </div>
          <div className="h-[360px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byDecile}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                <XAxis
                  dataKey="decile"
                  tick={AXIS_STYLE}
                  tickLine={false}
                  label={{ value: "Income decile", position: "insideBottom", offset: -12, style: AXIS_STYLE }}
                />
                <YAxis
                  tick={AXIS_STYLE}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={rentBurdenMode === "pct" ? (v) => `${v}%` : (v) => formatCurrency(v)}
                />
                <Tooltip content={<CustomTooltip formatter={rentBurdenMode === "pct" ? (v) => `${Number(v).toFixed(1)}%` : formatCurrency} />} />
                <Bar
                  dataKey={rentBurdenMode === "pct" ? "rent_to_income_pct" : "avg_rent"}
                  name={rentBurdenMode === "pct" ? "Rent as % of income" : "Average rent"}
                  fill={colors.primary[600]}
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <ChartLogo />
        </div>

        {byHhType.length > 0 && (
          <div className="section-card">
            <SectionHeading
              title="Average rent by household type"
              description="Average annual rent per household for renters, by family type."
            />
            <div className="h-[360px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={byHhType} layout="vertical" margin={{ left: 10, right: 30, top: 10, bottom: 10 }} barSize={28}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} horizontal={false} />
                  <XAxis
                    type="number"
                    tick={AXIS_STYLE}
                    tickLine={false}
                    tickFormatter={(v) => `£${(v / 1000).toFixed(0)}k`}
                  />
                  <YAxis
                    type="category"
                    dataKey="hh_type"
                    tick={{ ...AXIS_STYLE, fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                    width={160}
                  />
                  <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  <Bar dataKey="avg_rent" name="Average rent" fill={colors.primary[600]} radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ChartLogo />
          </div>
        )}
      </div>

      {/* Row 3: Average rent by region (half-width) */}
      <div className="grid gap-8 xl:grid-cols-2">
        {sortedRegions.length > 0 && (
          <div className="section-card">
            <SectionHeading
              title="Average rent by region"
              description="Average annual rent per renter household by UK region."
            />
            <div className="h-[420px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sortedRegions} layout="vertical" margin={{ left: 10, right: 30, top: 10, bottom: 10 }} barSize={20}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} horizontal={false} />
                  <XAxis
                    type="number"
                    tick={AXIS_STYLE}
                    tickLine={false}
                    tickFormatter={(v) => `£${(v / 1000).toFixed(0)}k`}
                  />
                  <YAxis
                    type="category"
                    dataKey="region"
                    tick={{ ...AXIS_STYLE, fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                    width={160}
                  />
                  <Tooltip content={<CustomTooltip formatter={formatCurrency} />} />
                  <Bar dataKey="avg_rent" name="Average rent" fill={colors.primary[600]} radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ChartLogo />
          </div>
        )}
      </div>

      {/* ================================================================ */}
      {/* SECTION 2: HOUSING BENEFITS                                     */}
      {/* ================================================================ */}
      <div className="border-t border-slate-200 pt-10">
        <div className="flex items-start justify-between">
          <SectionHeading
            title="Housing benefit spending"
            description="This section shows government spending on Housing Benefit (legacy) and the UC housing element, and how it is distributed across income deciles and tenure types."
          />
          <BenefitToggle mode={benefitMode} setMode={setBenefitMode} />
        </div>
      </div>

      {/* % receiving benefits + benefit spending by tenure — side by side */}
      <div className="grid gap-8 xl:grid-cols-2">
        <div className="section-card">
          <SectionHeading
            title={`% receiving ${benefitLabel} by decile`}
            description={`Share of households receiving ${benefitMode === "hb" ? "Housing Benefit (legacy, mostly pensioners)" : "Universal Credit"} by income decile.`}
          />
          <div className="h-[360px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byDecile}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                <XAxis
                  dataKey="decile"
                  tick={AXIS_STYLE}
                  tickLine={false}
                  label={{ value: "Income decile", position: "insideBottom", offset: -12, style: AXIS_STYLE }}
                />
                <YAxis
                  tick={AXIS_STYLE}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip content={<CustomTooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />} />
                <Bar
                  dataKey={benefitMode === "hb" ? "pct_receiving_hb" : "pct_receiving_uc_housing"}
                  name={benefitLabel}
                  fill={colors.primary[600]}
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <ChartLogo />
        </div>

        <div className="section-card">
          <SectionHeading
            title={`${benefitLabel} spending by tenure`}
            description={`Total ${benefitLabel} spending by renter tenure type.`}
          />
          <div className="h-[360px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byTenure}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                <XAxis dataKey="tenure" tick={AXIS_STYLE} tickLine={false} />
                <YAxis
                  tick={AXIS_STYLE}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `£${v}bn`}
                />
                <Tooltip content={<CustomTooltip formatter={(v) => `£${Number(v).toFixed(1)}bn`} />} />
                <Bar
                  dataKey={benefitMode === "hb" ? "hb_bn" : "uc_housing_bn"}
                  name={benefitLabel}
                  fill={colors.primary[600]}
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <ChartLogo />
        </div>
      </div>

      {/* Distributional impact of HB/UC by decile (half-width) */}
      <div className="grid gap-8 xl:grid-cols-2">
        <div className="section-card">
          <SectionHeading
            title={`Distributional impact of ${benefitMode === "hb" ? "HB" : "UC housing"} by decile`}
            description={`Relative change in household income from ${benefitLabel}. Deciles ranked by income excluding the benefit.`}
          />
          <div className="h-[360px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={benefitMode === "hb" ? distImpact.hb : distImpact.uc_housing}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
                <XAxis
                  dataKey="decile"
                  tick={AXIS_STYLE}
                  tickLine={false}
                  label={{ value: "Income decile", position: "insideBottom", offset: -12, style: AXIS_STYLE }}
                />
                <YAxis
                  tick={AXIS_STYLE}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `+${v}%`}
                />
                <Tooltip content={<CustomTooltip formatter={(v) => `+${Number(v).toFixed(1)}%`} />} />
                <Bar
                  dataKey="pct_of_income"
                  name={benefitLabel}
                  fill={colors.primary[600]}
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <ChartLogo />
        </div>
      </div>
    </div>
  );
}
