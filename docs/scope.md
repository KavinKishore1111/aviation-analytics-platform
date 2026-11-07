# Project Scope

## Positioning

US domestic aviation analytics platform integrating BTS on-time performance, OurAirports metadata, and Open-Meteo ERA5 weather reanalysis. Single-source fact table (BTS) by design — coherent over fragmented. Geographic coverage is US-only including HI, AK, PR, USVI, Guam, and Northern Mariana Islands (all report under US state codes in BTS).

## Historical Window

**Decision:** 12 months, 2025-08-01 → 2026-07-31.

**Rationale:** 12-month pull for one airport returned 8,760 rows, 0 nulls, no rate limit. Scaling to 352 airports = 352 API calls (one per airport, whole year) — feasible. 24 months adds no analytical depth for the portfolio.

## Data Sources

| Source | Type | Cadence | Role |
|---|---|---|---|
| BTS On-Time Performance | CSV download | Monthly | Fact source (flight-level) |
| OurAirports | CSV download | Nightly | Airport dimension |
| Open-Meteo Archive API | REST API | Static historical | Weather dimension |

**Explicitly excluded:** OpenSky, EUROCONTROL, OAG, DGCA India, Pro Flight Search — add complexity without improving US-domestic analytical depth.

## Data Honesty Rules

1. Weather is **ERA5 modeled reanalysis** at the airport grid cell — NOT station observation. Document this in README and every weather mart.
2. Weather ↔ delay relationships are **correlational, not causal**. Never write "weather caused delay."
3. BTS delay cause codes are **carrier-reported**, populated only for flights delayed ≥15 min. Null = not applicable, never impute zero.
4. Airport mapping is verified at 352/352 (100%), zero IATA collisions, with 31 territory/non-contiguous airports confirmed via ICAO + coordinates.
5. If an identifier cannot be reliably mapped, flag it, count it, exclude it explicitly — no silent drops.