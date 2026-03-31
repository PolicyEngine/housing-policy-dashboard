# UK Housing Policy Dashboard

Interactive dashboard estimating the fiscal and distributional effects of UK housing policies using [PolicyEngine UK](https://github.com/PolicyEngine/policyengine-uk) microsimulation.

**Live dashboard**: https://housing-policy-dashboard.vercel.app

## Policies modelled

1. **Blanket rent reduction** — immediate 10% cut to all private rents
2. **LHA unfreeze** — restore rates to 30th percentile of local market rents
3. **SAR abolition** — abolish Shared Accommodation Rate from age 18
4. **Social rent cap** — 5% cap on council and housing association rents
5. **Rent control (CPI+1% cap)** — cap annual private rent increases at CPI+1% (5%, 10%, 15% below market scenarios)

## Quick start

### Python pipeline

```bash
pip install -e ".[dev,simulation]"
rent-control-build --sync-dashboard
```

### Dashboard

```bash
cd dashboard
npm install
npm run dev
```

## Architecture

```
rent-control/
├── src/rent_control/     # Python pipeline + analysis
├── tests/                # Unit tests for analysis functions
├── data/                 # Generated JSON output
└── dashboard/            # Next.js dashboard (deployed to Vercel)
```

## Deployment

The dashboard auto-deploys to Vercel on push to `main`.

## Data sources

- Enhanced Family Resources Survey 2023-24 via PolicyEngine UK
- BRMA/LHA rates from DWP Stat-Xplore
- ONS private rent indices

## Running tests

```bash
pytest
```
