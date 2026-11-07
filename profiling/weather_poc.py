import requests
import pandas as pd

# ---------- 1. Fetch weather ----------
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 41.9786,
    "longitude": -87.9048,
    "start_date": "2026-08-01",
    "end_date": "2026-08-07",
    "hourly": "temperature_2m,precipitation,wind_speed_10m,relative_humidity_2m",
    "timezone": "America/Chicago",
}

resp = requests.get(url, params=params, timeout=60)
resp.raise_for_status()
payload = resp.json()

weather = pd.DataFrame(payload["hourly"])
weather["time"] = pd.to_datetime(weather["time"])

print("=== Weather PoC: ORD 2026-08-01 to 2026-08-07 ===")
print(f"Hourly rows returned: {len(weather)}")
print(f"Min time: {weather['time'].min()}")
print(f"Max time: {weather['time'].max()}")
print(f"Null counts:\n{weather.isna().sum()}")

# ---------- 2. BTS ORD departures on 2026-08-01 ----------
bts = pd.read_csv("data/raw/bts_aug2026.csv", dtype=str)
ord_dep = bts[(bts["ORIGIN"] == "ORD") & (bts["FL_DATE"] == "8/1/2026 12:00:00 AM")].copy()

print(f"\n=== BTS ORD departures on 2026-08-01: {len(ord_dep)} flights ===")

# Parse CRS_DEP_TIME (hhmm string) -> hour
# e.g. "0900" -> 9, "2359" -> 23
ord_dep["dep_hour"] = pd.to_datetime(
    ord_dep["CRS_DEP_TIME"].str.zfill(4), format="%H%M"
).dt.hour

# Build a local timestamp: date + hour
ord_dep["local_ts"] = pd.to_datetime("2026-08-01") + pd.to_timedelta(ord_dep["dep_hour"], unit="h")

# ---------- 3. Alignment check ----------
weather_hours = set(weather["time"])
ord_dep["matched"] = ord_dep["local_ts"].isin(weather_hours)

matched = ord_dep["matched"].sum()
total = len(ord_dep)
print(f"Aligned: {matched}/{total} ({matched/total*100:.2f}%)")

if matched < total:
    print("Unmatched rows:")
    print(ord_dep.loc[~ord_dep["matched"], ["CRS_DEP_TIME", "dep_hour", "local_ts"]])

# ---------- 4. Sample side-by-side ----------
print("\n=== Sample aligned row ===")
sample = ord_dep[ord_dep["matched"]].iloc[0]
w_row = weather[weather["time"] == sample["local_ts"]].iloc[0]
print(f"BTS: CRS_DEP_TIME={sample['CRS_DEP_TIME']}, ARR_DELAY={sample['ARR_DELAY']}, "
      f"CANCELLED={sample['CANCELLED']}")
print(f"Weather @ {w_row['time']}: temp={w_row['temperature_2m']}C, "
      f"precip={w_row['precipitation']}mm, wind={w_row['wind_speed_10m']}km/h, "
      f"humidity={w_row['relative_humidity_2m']}%")