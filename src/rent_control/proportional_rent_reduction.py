"""Generate proportional_rent_reduction.json for the dashboard.

Mechanical equal-proportional private rent reduction scenario, England,
2029-30. The numbers and Plotly figure data below are extracted from the
microsimulation run; this module just emits them as JSON.

This is a scenario, not a microsim of a per-tenancy rent-growth cap.
The cap's per-household incidence depends on tenancy-level baseline rent
growth, tenancy duration, and turnover — none observed in the FRS
cross-section. Do not interpret the decile chart as the cap's
distributional incidence.

Run:
    python -m rent_control.proportional_rent_reduction
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_OUTPUT = Path("dashboard/public/data/proportional_rent_reduction.json")

TARGET_YEAR = 2029

# ── Section 1: dispersion sensitivity ──────────────────────────────────────

DISPERSION_UNIFORM = [
    {"scenario": "(a) Uniform", "description": "every tenancy +4%",
     "avg_baseline": "4.0%", "avg_capped": "2.0%", "avg_reduction_pp": "2.0 pp"},
    {"scenario": "(b) Narrow", "description": "50% at +2%, 50% at +6%",
     "avg_baseline": "4.0%", "avg_capped": "2.0%", "avg_reduction_pp": "2.0 pp"},
    {"scenario": "(c) Wide", "description": "50% flat (0%), 50% at +8%",
     "avg_baseline": "4.0%", "avg_capped": "1.0%", "avg_reduction_pp": "3.0 pp"},
]

DISPERSION_NORMAL = [
    {"dispersion": "Tight (sd=1%)", "avg_baseline": "3.34%", "avg_capped": "1.96%",
     "actual_reduction_pp": "1.38 pp", "uniform_assumes_pp": "1.34 pp"},
    {"dispersion": "Moderate (sd=3%)", "avg_baseline": "3.34%", "avg_capped": "1.35%",
     "actual_reduction_pp": "1.98 pp", "uniform_assumes_pp": "1.34 pp"},
    {"dispersion": "Wide (sd=5%)", "avg_baseline": "3.32%", "avg_capped": "0.59%",
     "actual_reduction_pp": "2.73 pp", "uniform_assumes_pp": "1.34 pp"},
    {"dispersion": "Very wide (sd=7%)", "avg_baseline": "3.36%", "avg_capped": "-0.17%",
     "actual_reduction_pp": "3.52 pp", "uniform_assumes_pp": "1.34 pp"},
]

# ── Section 2: two-household toy ───────────────────────────────────────────

TWO_HH_DISPERSION = [
    {"distribution": "Uniform — both face 4%",  "household": "Lower-rent (£6k)",  "market_rise": "4.0%", "baseline_rent": 6240,  "reform_rent": 6120,  "saving": 120},
    {"distribution": "Uniform — both face 4%",  "household": "Higher-rent (£30k)", "market_rise": "4.0%", "baseline_rent": 31200, "reform_rent": 30600, "saving": 600},
    {"distribution": "Wide — lower 0%, higher 8%", "household": "Lower-rent (£6k)",  "market_rise": "0.0%", "baseline_rent": 6000,  "reform_rent": 6000,  "saving": 0},
    {"distribution": "Wide — lower 0%, higher 8%", "household": "Higher-rent (£30k)", "market_rise": "8.0%", "baseline_rent": 32400, "reform_rent": 30600, "saving": 1800},
    {"distribution": "Wide — lower 8%, higher 0%", "household": "Lower-rent (£6k)",  "market_rise": "8.0%", "baseline_rent": 6480,  "reform_rent": 6120,  "saving": 360},
    {"distribution": "Wide — lower 8%, higher 0%", "household": "Higher-rent (£30k)", "market_rise": "0.0%", "baseline_rent": 30000, "reform_rent": 30000, "saving": 0},
]

TWO_HH_AGGREGATE = [
    {"distribution": "Uniform — both face 4%",   "total_saving": 720,  "pct_combined_rent": "2.0%"},
    {"distribution": "Wide — lower 0%, higher 8%", "total_saving": 1800, "pct_combined_rent": "5.0%"},
    {"distribution": "Wide — lower 8%, higher 0%", "total_saving": 360,  "pct_combined_rent": "1.0%"},
]

# ── Section 3.1: baseline rent-growth parameters ───────────────────────────

RENT_GROWTH_RATES = [
    {"year": 2022, "cpi": "9.07%", "blended": "3.47%", "social": "5.00%", "iphrp": "5.04%", "private_pe": "5.04%"},
    {"year": 2023, "cpi": "7.30%", "blended": "5.75%", "social": "7.00%", "iphrp": "8.10%", "private_pe": "8.10%"},
    {"year": 2024, "cpi": "2.50%", "blended": "7.16%", "social": "8.30%", "iphrp": "8.61%", "private_pe": "8.61%"},
    {"year": 2025, "cpi": "3.40%", "blended": "5.42%", "social": "3.50%", "iphrp": "—",     "private_pe": "5.42%"},
    {"year": 2026, "cpi": "2.30%", "blended": "3.34%", "social": "4.40%", "iphrp": "—",     "private_pe": "3.34%"},
    {"year": 2027, "cpi": "2.00%", "blended": "3.02%", "social": "3.30%", "iphrp": "—",     "private_pe": "3.02%"},
    {"year": 2028, "cpi": "2.00%", "blended": "2.30%", "social": "3.00%", "iphrp": "—",     "private_pe": "2.30%"},
    {"year": 2029, "cpi": "2.00%", "blended": "2.38%", "social": "3.00%", "iphrp": "—",     "private_pe": "2.38%"},
    {"year": 2030, "cpi": "2.00%", "blended": "2.58%", "social": "3.00%", "iphrp": "—",     "private_pe": "2.58%"},
]

# ── Section 3.2: alternative aggregate growth path ─────────────────────────

ALTERNATIVE_AGGREGATE_PATH = [
    {"year": 2022, "cpi_lag": "4.00%", "baseline_yoy": "5.04%", "scenario_yoy": "5.04%", "below_baseline": "—"},
    {"year": 2023, "cpi_lag": "9.07%", "baseline_yoy": "8.10%", "scenario_yoy": "8.10%", "below_baseline": "—"},
    {"year": 2024, "cpi_lag": "7.30%", "baseline_yoy": "8.61%", "scenario_yoy": "8.61%", "below_baseline": "—"},
    {"year": 2025, "cpi_lag": "2.50%", "baseline_yoy": "5.42%", "scenario_yoy": "5.42%", "below_baseline": "—"},
    {"year": 2026, "cpi_lag": "3.40%", "baseline_yoy": "3.34%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
    {"year": 2027, "cpi_lag": "2.30%", "baseline_yoy": "3.02%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
    {"year": 2028, "cpi_lag": "2.00%", "baseline_yoy": "2.30%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
    {"year": 2029, "cpi_lag": "2.00%", "baseline_yoy": "2.38%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
    {"year": 2030, "cpi_lag": "2.00%", "baseline_yoy": "2.58%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
]

# ── Section 3.3: cumulative rent index ─────────────────────────────────────

RENT_INDEX_YEARS = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
RENT_INDEX_BASELINE = [100.00, 105.42, 108.94, 112.23, 114.81, 117.54, 120.58]
RENT_INDEX_SCENARIO = [100.00, 105.42, 107.53, 109.68, 111.87, 114.11, 116.39]
SCENARIO_START = 2026

CUMULATIVE_RENT_INDEX = [
    {"year": y, "baseline_index": b, "scenario_index": s,
     "gap_vs_baseline": f"{(s/b - 1) * 100:.2f}%"}
    for y, b, s in zip(RENT_INDEX_YEARS, RENT_INDEX_BASELINE, RENT_INDEX_SCENARIO)
]

# ── Section 3.4: two-household projection to 2029 ──────────────────────────

TWO_HH_PROJECTION = [
    {"household": "Lower-rent (£6k in 2024)",  "rent_2024": 6000,  "baseline_2029": 7053,  "scenario_2029": 6847,  "rent_reduction": 206,  "reduction_pct": "2.92%"},
    {"household": "Higher-rent (£30k in 2024)", "rent_2024": 30000, "baseline_2029": 35263, "scenario_2029": 34233, "rent_reduction": 1030, "reduction_pct": "2.92%"},
]

# ── Section 4: distributional results ──────────────────────────────────────

HEADLINE = {
    "households_in_scope_m": 6.11,
    "aggregate_ahc_gain_gbp_bn": 2.79,
    "mean_gain_per_household_gbp": 456,
}

DECILE_MEANS = [
    {"decile": 1,  "mean_delta_ahc_gbp": 297.15},
    {"decile": 2,  "mean_delta_ahc_gbp": 241.10},
    {"decile": 3,  "mean_delta_ahc_gbp": 453.38},
    {"decile": 4,  "mean_delta_ahc_gbp": 302.49},
    {"decile": 5,  "mean_delta_ahc_gbp": 341.18},
    {"decile": 6,  "mean_delta_ahc_gbp": 366.97},
    {"decile": 7,  "mean_delta_ahc_gbp": 479.48},
    {"decile": 8,  "mean_delta_ahc_gbp": 523.67},
    {"decile": 9,  "mean_delta_ahc_gbp": 642.96},
    {"decile": 10, "mean_delta_ahc_gbp": 897.15},
]

# ── Plotly figures ─────────────────────────────────────────────────────────

_FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
_FONT_DARK = "#1f2937"
_FONT_MUTED = "#6b7280"
_GRID = "#f1f5f9"
_AXIS_LINE = "#e5e7eb"
_TEAL = "#2C8E8E"
_TEAL_DARK = "#1f6e6e"
_NAVY = "#1e3a5f"


def _axis_title(text: str) -> dict:
    return {
        "text": text,
        "font": {"family": _FONT_FAMILY, "size": 13, "color": _FONT_DARK},
        "standoff": 12,
    }


def _tickfont() -> dict:
    return {"family": _FONT_FAMILY, "size": 12, "color": _FONT_DARK}


RENT_INDEX_FIGURE = {
    "data": [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Baseline (OBR forecast)",
            "x": RENT_INDEX_YEARS,
            "y": RENT_INDEX_BASELINE,
            "line": {"color": _NAVY, "width": 2.8, "shape": "spline", "smoothing": 0.4},
            "marker": {"size": 7, "color": _NAVY, "line": {"width": 0}},
            "hovertemplate": "<b>%{y:.2f}</b><extra>Baseline</extra>",
        },
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": "Scenario (2% from 2026)",
            "x": RENT_INDEX_YEARS,
            "y": RENT_INDEX_SCENARIO,
            "line": {"color": _TEAL, "width": 2.8, "shape": "spline", "smoothing": 0.4},
            "marker": {"size": 7, "color": _TEAL, "line": {"width": 0}},
            "hovertemplate": "<b>%{y:.2f}</b><extra>Scenario</extra>",
        },
    ],
    "layout": {
        "title": {
            "text": "Private rent index — baseline vs alternative aggregate path",
            "font": {"family": _FONT_FAMILY, "size": 16, "color": _FONT_DARK},
            "x": 0.5,
            "xanchor": "center",
            "y": 0.96,
        },
        "xaxis": {
            "title": _axis_title("Year"),
            "dtick": 1,
            "showgrid": False,
            "showline": True,
            "linecolor": _AXIS_LINE,
            "ticks": "outside",
            "tickcolor": _AXIS_LINE,
            "tickfont": _tickfont(),
        },
        "yaxis": {
            "title": _axis_title("Rent index (2024 = 100)"),
            "showgrid": True,
            "gridcolor": _GRID,
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": _tickfont(),
        },
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font": {"family": _FONT_FAMILY, "color": _FONT_DARK},
        "margin": {"l": 70, "r": 30, "t": 70, "b": 90},
        "legend": {
            "orientation": "h",
            "y": -0.18,
            "x": 0.5,
            "xanchor": "center",
            "font": {"family": _FONT_FAMILY, "size": 13, "color": _FONT_DARK},
            "bgcolor": "rgba(0,0,0,0)",
        },
        "hovermode": "x unified",
        "hoverlabel": {
            "bgcolor": "white",
            "bordercolor": _AXIS_LINE,
            "font": {"family": _FONT_FAMILY, "size": 12, "color": _FONT_DARK},
        },
        "shapes": [
            {
                "type": "line",
                "x0": SCENARIO_START,
                "x1": SCENARIO_START,
                "xref": "x",
                "y0": 0,
                "y1": 1,
                "yref": "y domain",
                "line": {"color": "#9ca3af", "dash": "dash", "width": 1.5},
                "opacity": 0.7,
            }
        ],
        "annotations": [
            {
                "x": SCENARIO_START,
                "y": 1.02,
                "xref": "x",
                "yref": "y domain",
                "xanchor": "right",
                "yanchor": "bottom",
                "text": "Scenario starts 2026",
                "showarrow": False,
                "font": {"family": _FONT_FAMILY, "size": 11, "color": _FONT_MUTED},
            }
        ],
    },
}

DECILE_CHART_FIGURE = {
    "data": [
        {
            "type": "bar",
            "x": [d["decile"] for d in DECILE_MEANS],
            "y": [d["mean_delta_ahc_gbp"] for d in DECILE_MEANS],
            "marker": {
                "color": _TEAL,
                "line": {"color": _TEAL_DARK, "width": 0},
            },
            "text": [f"£{round(d['mean_delta_ahc_gbp']):,}" for d in DECILE_MEANS],
            "textposition": "outside",
            "textfont": {"family": _FONT_FAMILY, "size": 11, "color": _FONT_DARK},
            "cliponaxis": False,
            "hovertemplate": "Decile %{x}<br><b>£%{y:,.0f}</b> per year<extra></extra>",
        }
    ],
    "layout": {
        "title": {
            "text": "Mean change in AHC household net income, by gross-income decile",
            "font": {"family": _FONT_FAMILY, "size": 16, "color": _FONT_DARK},
            "x": 0.5,
            "xanchor": "center",
            "y": 0.96,
        },
        "xaxis": {
            "title": _axis_title("Gross household income decile (1 = lowest)"),
            "dtick": 1,
            "tickmode": "linear",
            "tick0": 1,
            "showgrid": False,
            "showline": True,
            "linecolor": _AXIS_LINE,
            "ticks": "outside",
            "tickcolor": _AXIS_LINE,
            "tickfont": _tickfont(),
        },
        "yaxis": {
            "title": _axis_title("Change in AHC net income (£/year)"),
            "showgrid": True,
            "gridcolor": _GRID,
            "zeroline": True,
            "zerolinecolor": _AXIS_LINE,
            "zerolinewidth": 1,
            "tickprefix": "£",
            "tickformat": ",",
            "tickfont": _tickfont(),
        },
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font": {"family": _FONT_FAMILY, "color": _FONT_DARK},
        "margin": {"l": 70, "r": 30, "t": 70, "b": 80},
        "bargap": 0.25,
        "showlegend": False,
        "hoverlabel": {
            "bgcolor": "white",
            "bordercolor": _AXIS_LINE,
            "font": {"family": _FONT_FAMILY, "size": 12, "color": _FONT_DARK},
        },
    },
}

# ── Assembled results ──────────────────────────────────────────────────────

RESULTS = {
    "target_year": TARGET_YEAR,
    "headline": HEADLINE,
    "decile_means": DECILE_MEANS,
    "tables": {
        "dispersion_uniform": DISPERSION_UNIFORM,
        "dispersion_normal": DISPERSION_NORMAL,
        "two_household_dispersion": TWO_HH_DISPERSION,
        "two_household_aggregate": TWO_HH_AGGREGATE,
        "rent_growth_rates": RENT_GROWTH_RATES,
        "alternative_aggregate_path": ALTERNATIVE_AGGREGATE_PATH,
        "cumulative_rent_index": CUMULATIVE_RENT_INDEX,
        "two_household_projection": TWO_HH_PROJECTION,
    },
    "figures": {
        "rent_index": RENT_INDEX_FIGURE,
        "decile_change_ahc": DECILE_CHART_FIGURE,
    },
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write the proportional rent reduction JSON results."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(RESULTS, indent=2) + "\n")
    print(f"Wrote {args.output}")
    print(
        "Headline: "
        f"{HEADLINE['households_in_scope_m']}m HH, "
        f"£{HEADLINE['aggregate_ahc_gain_gbp_bn']}bn aggregate, "
        f"£{HEADLINE['mean_gain_per_household_gbp']} mean."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
