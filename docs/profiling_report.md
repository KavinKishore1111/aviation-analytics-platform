# Phase 1 Profiling Report

## BTS Flight Data — August 2026

- Shape: **(608,389, 30)**
- Date range: **2026-08-01 to 2026-08-31** (0 parse failures)
- Distinct airports: **352** (origin = dest = union)
- Distinct airlines: **12** (WN 116k, DL 91k, AA 84k, OO 75k, UA 74k, AS 31k, YX 31k, MQ 29k, B6 24k, OH 21k, F9 20k, G4 10k)
- CANCELLED: **11,313 (1.86%)**
- DIVERTED: **2,869 (0.47%)**
- CANCELLATION_CODE (among cancelled): A=3,119, B=5,274, C=2,920, D=0
- Delay-cause non-null: **159,636** — exactly equals `ARR_DEL15=1` count ✅

### Null rates (key columns)

| Column group | Null % |
|---|---|
| Delay cause (5 fields) | 73.76% — null = not delayed ≥15 min, never impute |
| CANCELLATION_CODE | 98.14% — populated only when CANCELLED=1 |
| ARR_DELAY / ARR_DELAY_NEW / ARR_DEL15 | 2.33% — null on cancelled + diverted |
| DEP_DELAY / DEP_DELAY_NEW / DEP_DEL15 | 1.75% — null on cancelled |
| DEP_TIME | 1.74% |
| ARR_TIME | 1.94% |
| All other columns | 0.00% |

## Airport Mapping Verification

- BTS airports: 352
- Mapped to OurAirports: **352 (100.00%)**
- Unmapped: **0**
- IATA duplicate collisions globally: **0**
- IATA duplicate collisions among 352 airports: **0**
- Spot-check (ATL, LAX, ORD, DFW, DEN, JFK, SFO, SEA, MIA, BOS): **10/10 correct** coordinates + ICAO
- Check 1 "outside contiguous bbox": **31** — all legitimate HI (5), AK (19), PR/VI (5), Guam/Saipan (2). All confirmed correct by ICAO ident.
- Check 2 state mismatches: **8** — all state-code labeling differences (DCA→US-DC, VI→VI-ST/SC, PR→PR-U-A, TT→GU-U-A/MP-U-A). Same airports, different codes.

**Canonical decision:** Use OurAirports `iso_region` as canonical state field. BTS `TT` is not ISO and does not correspond to GU/MP.

## Weather PoC (ORD, 2026-08-01 to 2026-08-07)

- Hourly rows: **168** (7 × 24) ✅
- Time range: **2026-08-01 00:00 → 2026-08-07 23:00** (America/Chicago)
- Nulls: **0** across all 4 variables ✅
- BTS ORD departures on 2026-08-01: **1,013**
- Aligned to weather hour: **1,013/1,013 (100%)** ✅
- Sample: CRS_DEP_TIME=2259 with ARR_DELAY=87 → matched 22:00 weather row (20°C, 0mm, 15.5 km/h, 91% humidity)

## 12-Month Feasibility Test

- ORD 2025-08-01 → 2026-07-31: **8,760 rows**, 0 nulls, no rate limit ✅
- Scaling: 352 airports × 1 call each = **352 API calls** for full weather history
- Historical window **LOCKED**: 12 months, 2025-08-01 → 2026-07-31

## Phase 1 Completion Checklist

- [x] BTS profiling complete
- [x] Airport mapping verified 100%, 0 collisions
- [x] Open-Meteo PoC aligned 100%
- [x] 12-month pull feasible
- [x] data_dictionary.md
- [x] scope.md
- [x] profiling_report.md
- [x] airport_mapping.csv
- [ ] Committed to Git ← **do this next**