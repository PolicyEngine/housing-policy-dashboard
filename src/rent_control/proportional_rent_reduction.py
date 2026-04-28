"""Generate proportional_rent_reduction.json for the dashboard.

Mechanical equal-proportional private rent reduction scenario and
heterogeneous no-moves sensitivity, England, 2029-30. The household-level
microsimulation outputs are extracted from PolicyEngine UK using the
enhanced FRS 2023-24 and the current private-rent path.

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
    {"year": 2022, "cpi": "9.07%", "blended": "3.47%", "social": "1.60%", "iphrp": "4.15%", "private_pe": "4.15%"},
    {"year": 2023, "cpi": "7.30%", "blended": "5.75%", "social": "4.10%", "iphrp": "7.17%", "private_pe": "7.17%"},
    {"year": 2024, "cpi": "2.50%", "blended": "7.16%", "social": "7.20%", "iphrp": "8.72%", "private_pe": "8.72%"},
    {"year": 2025, "cpi": "3.40%", "blended": "5.42%", "social": "8.00%", "iphrp": "—",     "private_pe": "6.40%"},
    {"year": 2026, "cpi": "2.30%", "blended": "3.34%", "social": "4.80%", "iphrp": "—",     "private_pe": "2.07%"},
    {"year": 2027, "cpi": "2.00%", "blended": "3.02%", "social": "3.30%", "iphrp": "—",     "private_pe": "2.78%"},
    {"year": 2028, "cpi": "2.00%", "blended": "2.30%", "social": "3.00%", "iphrp": "—",     "private_pe": "1.69%"},
    {"year": 2029, "cpi": "2.00%", "blended": "2.38%", "social": "3.00%", "iphrp": "—",     "private_pe": "1.84%"},
    {"year": 2030, "cpi": "2.00%", "blended": "2.58%", "social": "3.00%", "iphrp": "—",     "private_pe": "2.21%"},
]

# ── Section 3.2: alternative aggregate growth path ─────────────────────────

ALTERNATIVE_AGGREGATE_PATH = [
    {"year": 2022, "cpi_lag": "4.00%", "baseline_yoy": "4.15%", "scenario_yoy": "4.15%", "below_baseline": "—"},
    {"year": 2023, "cpi_lag": "9.07%", "baseline_yoy": "7.17%", "scenario_yoy": "7.17%", "below_baseline": "—"},
    {"year": 2024, "cpi_lag": "7.30%", "baseline_yoy": "8.72%", "scenario_yoy": "8.72%", "below_baseline": "—"},
    {"year": 2025, "cpi_lag": "2.50%", "baseline_yoy": "6.40%", "scenario_yoy": "6.40%", "below_baseline": "—"},
    {"year": 2026, "cpi_lag": "3.40%", "baseline_yoy": "2.07%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
    {"year": 2027, "cpi_lag": "2.30%", "baseline_yoy": "2.78%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
    {"year": 2028, "cpi_lag": "2.00%", "baseline_yoy": "1.69%", "scenario_yoy": "1.69%", "below_baseline": "no"},
    {"year": 2029, "cpi_lag": "2.00%", "baseline_yoy": "1.84%", "scenario_yoy": "1.84%", "below_baseline": "no"},
    {"year": 2030, "cpi_lag": "2.00%", "baseline_yoy": "2.21%", "scenario_yoy": "2.00%", "below_baseline": "yes"},
]

# ── Section 3.3: cumulative rent index ─────────────────────────────────────

RENT_INDEX_YEARS = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
RENT_INDEX_BASELINE = [100.00, 106.40, 108.60, 111.61, 113.50, 115.59, 118.14]
RENT_INDEX_SCENARIO = [100.00, 106.40, 108.53, 110.70, 112.57, 114.64, 116.93]
SCENARIO_START = 2026

CUMULATIVE_RENT_INDEX = [
    {"year": y, "baseline_index": b, "scenario_index": s,
     "gap_vs_baseline": f"{(s/b - 1) * 100:.2f}%"}
    for y, b, s in zip(RENT_INDEX_YEARS, RENT_INDEX_BASELINE, RENT_INDEX_SCENARIO)
]

# ── Section 3.4: two-household projection to 2029 ──────────────────────────

TWO_HH_PROJECTION = [
    {"household": "Lower-rent (£6k in 2024)",  "rent_2024": 6000,  "baseline_2029": 6935,  "scenario_2029": 6878,  "rent_reduction": 57,  "reduction_pct": "0.82%"},
    {"household": "Higher-rent (£30k in 2024)", "rent_2024": 30000, "baseline_2029": 34676, "scenario_2029": 34392, "rent_reduction": 284, "reduction_pct": "0.82%"},
]

# ── Section 4: distributional results ──────────────────────────────────────

HEADLINE = {
    "households_in_scope_m": 5.63,
    "aggregate_ahc_gain_gbp_bn": 0.724,
    "mean_gain_per_household_gbp": 129,
}

DECILE_MEANS = [
    {"decile": 1,  "mean_delta_ahc_gbp": 103.73},
    {"decile": 2,  "mean_delta_ahc_gbp": 96.53},
    {"decile": 3,  "mean_delta_ahc_gbp": 103.66},
    {"decile": 4,  "mean_delta_ahc_gbp": 92.42},
    {"decile": 5,  "mean_delta_ahc_gbp": 119.06},
    {"decile": 6,  "mean_delta_ahc_gbp": 96.38},
    {"decile": 7,  "mean_delta_ahc_gbp": 124.53},
    {"decile": 8,  "mean_delta_ahc_gbp": 150.09},
    {"decile": 9,  "mean_delta_ahc_gbp": 182.46},
    {"decile": 10, "mean_delta_ahc_gbp": 213.19},
]

# ── Section 6: heterogeneous no-moves sensitivity ──────────────────────────

HETEROGENEOUS_SCENARIOS = [
    {
        "id": "uniform",
        "label": "Uniform aggregate analogue",
        "aggregate_rent_reduction_pct": 0.819,
        "aggregate_rent_saving_gbp_bn": 0.746,
        "aggregate_ahc_gain_gbp_bn": 0.724,
        "mean_gain_per_household_gbp": 129,
    },
    {
        "id": "higher_rent_growth",
        "label": "Higher growth for higher-rent tenancies",
        "aggregate_rent_reduction_pct": 4.886,
        "aggregate_rent_saving_gbp_bn": 4.451,
        "aggregate_ahc_gain_gbp_bn": 4.405,
        "mean_gain_per_household_gbp": 782,
    },
    {
        "id": "lower_rent_growth",
        "label": "Higher growth for lower-rent tenancies",
        "aggregate_rent_reduction_pct": 4.804,
        "aggregate_rent_saving_gbp_bn": 4.376,
        "aggregate_ahc_gain_gbp_bn": 3.997,
        "mean_gain_per_household_gbp": 710,
    },
    {
        "id": "higher_income_growth",
        "label": "Higher growth for higher-income renters",
        "aggregate_rent_reduction_pct": 4.693,
        "aggregate_rent_saving_gbp_bn": 4.275,
        "aggregate_ahc_gain_gbp_bn": 4.256,
        "mean_gain_per_household_gbp": 756,
    },
    {
        "id": "lower_income_growth",
        "label": "Higher growth for lower-income renters",
        "aggregate_rent_reduction_pct": 4.547,
        "aggregate_rent_saving_gbp_bn": 4.142,
        "aggregate_ahc_gain_gbp_bn": 3.915,
        "mean_gain_per_household_gbp": 695,
    },
    {
        "id": "random_growth",
        "label": "Random growth draw",
        "aggregate_rent_reduction_pct": 4.913,
        "aggregate_rent_saving_gbp_bn": 4.476,
        "aggregate_ahc_gain_gbp_bn": 4.288,
        "mean_gain_per_household_gbp": 762,
    },
]

HETEROGENEOUS_DECILE_MEANS = {
    "uniform": [
        {"decile": 1, "mean_delta_ahc_gbp": 103.73},
        {"decile": 2, "mean_delta_ahc_gbp": 96.53},
        {"decile": 3, "mean_delta_ahc_gbp": 103.66},
        {"decile": 4, "mean_delta_ahc_gbp": 92.42},
        {"decile": 5, "mean_delta_ahc_gbp": 119.06},
        {"decile": 6, "mean_delta_ahc_gbp": 96.38},
        {"decile": 7, "mean_delta_ahc_gbp": 124.53},
        {"decile": 8, "mean_delta_ahc_gbp": 150.09},
        {"decile": 9, "mean_delta_ahc_gbp": 182.46},
        {"decile": 10, "mean_delta_ahc_gbp": 213.19},
    ],
    "higher_rent_growth": [
        {"decile": 1, "mean_delta_ahc_gbp": 420.98},
        {"decile": 2, "mean_delta_ahc_gbp": 263.22},
        {"decile": 3, "mean_delta_ahc_gbp": 431.35},
        {"decile": 4, "mean_delta_ahc_gbp": 184.40},
        {"decile": 5, "mean_delta_ahc_gbp": 373.88},
        {"decile": 6, "mean_delta_ahc_gbp": 189.62},
        {"decile": 7, "mean_delta_ahc_gbp": 442.68},
        {"decile": 8, "mean_delta_ahc_gbp": 741.09},
        {"decile": 9, "mean_delta_ahc_gbp": 2074.92},
        {"decile": 10, "mean_delta_ahc_gbp": 2617.98},
    ],
    "lower_rent_growth": [
        {"decile": 1, "mean_delta_ahc_gbp": 802.29},
        {"decile": 2, "mean_delta_ahc_gbp": 876.21},
        {"decile": 3, "mean_delta_ahc_gbp": 987.58},
        {"decile": 4, "mean_delta_ahc_gbp": 916.48},
        {"decile": 5, "mean_delta_ahc_gbp": 774.88},
        {"decile": 6, "mean_delta_ahc_gbp": 933.70},
        {"decile": 7, "mean_delta_ahc_gbp": 732.11},
        {"decile": 8, "mean_delta_ahc_gbp": 501.36},
        {"decile": 9, "mean_delta_ahc_gbp": 492.31},
        {"decile": 10, "mean_delta_ahc_gbp": 126.79},
    ],
    "higher_income_growth": [
        {"decile": 1, "mean_delta_ahc_gbp": 0.00},
        {"decile": 2, "mean_delta_ahc_gbp": 0.00},
        {"decile": 3, "mean_delta_ahc_gbp": 0.00},
        {"decile": 4, "mean_delta_ahc_gbp": 0.00},
        {"decile": 5, "mean_delta_ahc_gbp": 36.19},
        {"decile": 6, "mean_delta_ahc_gbp": 134.48},
        {"decile": 7, "mean_delta_ahc_gbp": 405.89},
        {"decile": 8, "mean_delta_ahc_gbp": 1028.12},
        {"decile": 9, "mean_delta_ahc_gbp": 2013.55},
        {"decile": 10, "mean_delta_ahc_gbp": 3708.36},
    ],
    "lower_income_growth": [
        {"decile": 1, "mean_delta_ahc_gbp": 2621.45},
        {"decile": 2, "mean_delta_ahc_gbp": 1573.01},
        {"decile": 3, "mean_delta_ahc_gbp": 1197.95},
        {"decile": 4, "mean_delta_ahc_gbp": 709.57},
        {"decile": 5, "mean_delta_ahc_gbp": 584.53},
        {"decile": 6, "mean_delta_ahc_gbp": 196.85},
        {"decile": 7, "mean_delta_ahc_gbp": 100.13},
        {"decile": 8, "mean_delta_ahc_gbp": 2.80},
        {"decile": 9, "mean_delta_ahc_gbp": 0.00},
        {"decile": 10, "mean_delta_ahc_gbp": 0.00},
    ],
    "random_growth": [
        {"decile": 1, "mean_delta_ahc_gbp": 816.46},
        {"decile": 2, "mean_delta_ahc_gbp": 431.03},
        {"decile": 3, "mean_delta_ahc_gbp": 418.63},
        {"decile": 4, "mean_delta_ahc_gbp": 639.40},
        {"decile": 5, "mean_delta_ahc_gbp": 1100.60},
        {"decile": 6, "mean_delta_ahc_gbp": 407.73},
        {"decile": 7, "mean_delta_ahc_gbp": 546.21},
        {"decile": 8, "mean_delta_ahc_gbp": 988.08},
        {"decile": 9, "mean_delta_ahc_gbp": 493.94},
        {"decile": 10, "mean_delta_ahc_gbp": 1635.82},
    ],
}

HETEROGENEOUS_GROWTH_RANGES = [
    {
        "id": "uniform",
        "label": "Uniform aggregate analogue",
        "mean_current_rent_reduction_pct": 0.819,
        "growth_range_pct": "2026: 2.07% to 2.07%; 2027: 2.78% to 2.78%; 2028: 1.69% to 1.69%; 2029: 1.84% to 1.84%",
    },
    {
        "id": "higher_rent_growth",
        "label": "Higher growth for higher-rent tenancies",
        "mean_current_rent_reduction_pct": 4.886,
        "growth_range_pct": "2026: -5.09% to 9.91%; 2027: -4.46% to 10.54%; 2028: -5.64% to 9.36%; 2029: -5.57% to 9.43%",
    },
    {
        "id": "lower_rent_growth",
        "label": "Higher growth for lower-rent tenancies",
        "mean_current_rent_reduction_pct": 4.804,
        "growth_range_pct": "2026: -5.10% to 9.90%; 2027: -4.47% to 10.53%; 2028: -5.64% to 9.36%; 2029: -5.58% to 9.42%",
    },
    {
        "id": "higher_income_growth",
        "label": "Higher growth for higher-income renters",
        "mean_current_rent_reduction_pct": 4.693,
        "growth_range_pct": "2026: -5.14% to 9.86%; 2027: -4.51% to 10.49%; 2028: -5.68% to 9.32%; 2029: -5.61% to 9.39%",
    },
    {
        "id": "lower_income_growth",
        "label": "Higher growth for lower-income renters",
        "mean_current_rent_reduction_pct": 4.547,
        "growth_range_pct": "2026: -5.10% to 9.90%; 2027: -4.46% to 10.54%; 2028: -5.63% to 9.37%; 2029: -5.56% to 9.44%",
    },
    {
        "id": "random_growth",
        "label": "Random growth draw",
        "mean_current_rent_reduction_pct": 4.913,
        "growth_range_pct": "2026: -5.10% to 9.90%; 2027: -4.47% to 10.53%; 2028: -5.65% to 9.35%; 2029: -5.58% to 9.42%",
    },
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
_ORANGE = "#d97706"
_RED = "#b91c1c"
_GREEN = "#15803d"
_PURPLE = "#6d28d9"
_GRAY = "#6b7280"


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
            "name": "Scenario (aggregate cap analogue)",
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

_HETEROGENEOUS_COLORS = {
    "uniform": _NAVY,
    "higher_rent_growth": _ORANGE,
    "lower_rent_growth": _GREEN,
    "higher_income_growth": _RED,
    "lower_income_growth": _PURPLE,
    "random_growth": _GRAY,
}

HETEROGENEOUS_DECILE_CHART_FIGURE = {
    "data": [
        {
            "type": "scatter",
            "mode": "lines+markers",
            "name": scenario["label"],
            "x": [d["decile"] for d in HETEROGENEOUS_DECILE_MEANS[scenario["id"]]],
            "y": [
                d["mean_delta_ahc_gbp"]
                for d in HETEROGENEOUS_DECILE_MEANS[scenario["id"]]
            ],
            "line": {
                "color": _HETEROGENEOUS_COLORS[scenario["id"]],
                "width": 2.4,
            },
            "marker": {"size": 6, "color": _HETEROGENEOUS_COLORS[scenario["id"]]},
            "hovertemplate": (
                "%{fullData.name}<br>Decile %{x}<br>"
                "<b>£%{y:,.0f}</b> per year<extra></extra>"
            ),
        }
        for scenario in HETEROGENEOUS_SCENARIOS
    ],
    "layout": {
        "title": {
            "text": "AHC gain by decile under alternative imputed rent-growth allocations",
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
        "margin": {"l": 70, "r": 30, "t": 70, "b": 140},
        "legend": {
            "orientation": "h",
            "y": -0.28,
            "x": 0.5,
            "xanchor": "center",
            "font": {"family": _FONT_FAMILY, "size": 12, "color": _FONT_DARK},
            "bgcolor": "rgba(0,0,0,0)",
        },
        "hovermode": "x unified",
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
        "heterogeneous_scenarios": HETEROGENEOUS_SCENARIOS,
        "heterogeneous_growth_ranges": HETEROGENEOUS_GROWTH_RANGES,
    },
    "heterogeneous_decile_means": HETEROGENEOUS_DECILE_MEANS,
    "figures": {
        "rent_index": RENT_INDEX_FIGURE,
        "decile_change_ahc": DECILE_CHART_FIGURE,
        "heterogeneous_decile_change_ahc": HETEROGENEOUS_DECILE_CHART_FIGURE,
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
