# UK Rent Control Policy Dashboard

Interactive dashboard estimating the fiscal and distributional effects of UK rent control policies using [PolicyEngine UK](https://github.com/PolicyEngine/policyengine-uk) microsimulation.

**Live dashboard**: https://rent-control-pi.vercel.app

## Policies modelled

1. **Blanket private rent reduction** (5%, 10%, 15%, 20%)
2. **LHA unfreeze** (30th and 50th percentile)
3. **Shared Accommodation Rate reform** (revert to 25, abolish at 18)
4. **Social rent cap** (5%, 7%, 10% reduction)
5. **Scotland CPI+1% private rent cap** (3%, 5%, 10% effective reduction)

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
