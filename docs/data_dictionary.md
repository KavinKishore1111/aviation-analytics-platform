# Data Dictionary

## BTS Flight Data — August 2026, 608,389 rows, 352 airports, 12 airlines

| Column | dtype | Null % | Business meaning | Handling decision |
|---|---|---|---|---|
| FL_DATE | date | 0.00 | Flight date (local) | Parse format="%m/%d/%Y %I:%M:%S %p"; never infer |
| OP_UNIQUE_CARRIER | string | 0.00 | Unique carrier code | Primary airline key in dim_airlines |
| OP_CARRIER_FL_NUM | int | 0.00 | Flight number | Integer cast in staging |
| ORIGIN_AIRPORT_ID | int | 0.00 | DOT airport ID | Join key to dim_airports |
| ORIGIN | string | 0.00 | IATA code | Used for mapping fallback |
| ORIGIN_CITY_NAME | string | 0.00 | City name | Descriptive only |
| ORIGIN_STATE_ABR | string | 0.00 | State code | Use OurAirports iso_region as canonical |
| DEST_AIRPORT_ID | int | 0.00 | DOT airport ID | Join key to dim_airports |
| DEST | string | 0.00 | IATA code | Used for mapping fallback |
| DEST_CITY_NAME | string | 0.00 | City name | Descriptive only |
| DEST_STATE_ABR | string | 0.00 | State code | Use OurAirports iso_region as canonical |
| CRS_DEP_TIME | string(hhmm) | 0.00 | Scheduled local departure | zfill(4), parse to hour for weather join |
| DEP_TIME | string(hhmm) | 1.74 | Actual local departure | Null when cancelled |
| DEP_DELAY | float | 1.75 | Dep delay minutes, negative = early | Null when cancelled |
| DEP_DELAY_NEW | float | 1.75 | Dep delay, early set to 0 | Null when cancelled |
| DEP_DEL15 | float→bool | 1.75 | 1 = departure delay ≥ 15 min | Cast to boolean in staging |
| CRS_ARR_TIME | string(hhmm) | 0.00 | Scheduled local arrival | zfill(4) |
| ARR_TIME | string(hhmm) | 1.94 | Actual local arrival | Null when cancelled/diverted |
| ARR_DELAY | float | 2.33 | Arr delay minutes, negative = early | Null when cancelled/diverted; never fill 0 |
| ARR_DELAY_NEW | float | 2.33 | Arr delay, early set to 0 | Null when cancelled/diverted |
| ARR_DEL15 | float→bool | 2.33 | 1 = arrival delay ≥ 15 min | Cast to boolean; core KPI flag |
| CANCELLED | float→bool | 0.00 | 1 = cancelled | Cast to boolean |
| CANCELLATION_CODE | string | 98.14 | A=Carrier, B=Weather, C=NAS, D=Security | Populated ONLY when CANCELLED=1; null = not cancelled |
| DIVERTED | float→bool | 0.00 | 1 = diverted | Cast to boolean |
| CARRIER_DELAY | float | 73.76 | Carrier delay minutes | Populated ONLY when ARR_DEL15=1; null = not applicable — never impute 0 |
| WEATHER_DELAY | float | 73.76 | Weather delay minutes | Same |
| NAS_DELAY | float | 73.76 | NAS delay minutes | Same |
| SECURITY_DELAY | float | 73.76 | Security delay minutes | Same |
| LATE_AIRCRAFT_DELAY | float | 73.76 | Late aircraft delay minutes | Same |

## Open-Meteo Weather (ERA5 reanalysis) — 4 variables

**Nature of data:** Modeled reanalysis at the airport's grid coordinates, NOT on-site station observation. Associations with delays are correlational, not causal.

| Variable | Unit | Null rate (PoC) | Business meaning |
|---|---|---|---|
| temperature_2m | °C | 0.00 | Air temp at 2 m above ground |
| precipitation | mm | 0.00 | Hourly precipitation total |
| wind_speed_10m | km/h | 0.00 | Wind speed at 10 m |
| relative_humidity_2m | % | 0.00 | Relative humidity at 2 m |

## Critical caveats (document everywhere)

1. **String-vs-float trap.** BTS booleans arrive as `"0.00"`/`"1.00"` strings. `df[col] == "1"` silently fails. Cast with `pd.to_numeric(..., errors="coerce") == 1` or match exact `"1.00"`.
2. **Delay cause null ≠ zero.** Null means "flight was not delayed ≥15 min" — semantically "not applicable." Never `COALESCE(..., 0)` in dbt.
3. **Cancellation code null ≠ missing.** Null means "flight was not cancelled." Populated only when `CANCELLED = 1`.
4. **State code canonical source.** Use OurAirports `iso_region` (e.g., `US-NY`) for states; BTS uses `TT` for territories, which is not ISO.
5. **Weather hour convention.** Weather row labeled `22:00` covers the hour 22:00–22:59. A 22:59 departure reads the 22:00 row.