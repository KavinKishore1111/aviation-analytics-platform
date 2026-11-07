import pandas as pd
import sys
sys.stdout.reconfigure(encoding="utf-8")

# ---------- load mapping ----------
m = pd.read_csv("data/processed/airport_mapping.csv", dtype=str)
m["lat"] = pd.to_numeric(m["lat"], errors="coerce")
m["lon"] = pd.to_numeric(m["lon"], errors="coerce")

print("=" * 60)
print("CHECK 1 — US bounding box")
print("=" * 60)
not_us = m[(m["lat"] < 24) | (m["lat"] > 50) |
           (m["lon"] < -125) | (m["lon"] > -66) | m["lat"].isna() | m["lon"].isna()]
print(f"Airports outside US bbox or missing coords: {len(not_us)}")
if len(not_us):
    print(not_us[["bts_iata", "bts_city", "bts_state",
                  "ourairports_ident", "ourairports_city", "lat", "lon"]].to_string())

print("\n" + "=" * 60)
print("CHECK 2 — State consistency (BTS state vs OurAirports region)")
print("=" * 60)
m["ourair_region"] = m["ourairports_region"].str.extract(r"US-(\w+)")
mismatch = m[m["ourair_region"] != m["bts_state"]]
print(f"State mismatches: {len(mismatch)}")
if len(mismatch):
    print(mismatch[["bts_iata", "bts_state", "ourairports_ident",
                    "ourairports_region", "ourairports_city"]].to_string())

print("\n" + "=" * 60)
print("CHECK 3 — Spot-check 10 major airports")
print("=" * 60)
big = ["ATL", "LAX", "ORD", "DFW", "DEN", "JFK", "SFO", "SEA", "MIA", "BOS"]
spot = m[m["bts_iata"].isin(big)][[
    "bts_iata", "bts_city", "bts_state",
    "ourairports_ident", "ourairports_city", "ourairports_region", "lat", "lon"
]].sort_values("bts_iata")
print(spot.to_string(index=False))

print("\n" + "=" * 60)
print("CHECK 4 — IATA duplicate collisions in OurAirports")
print("=" * 60)
ourair = pd.read_csv("data/raw/airports.csv", dtype=str)
ourair_iata = ourair.dropna(subset=["iata_code"])
dupes = ourair_iata.groupby("iata_code").size()
dupes = dupes[dupes > 1]
print(f"IATA codes appearing >1 time globally: {len(dupes)}")
bts_iata = set(m["bts_iata"])
collisions = dupes[dupes.index.isin(bts_iata)]
print(f"Collisions among your 352 airports: {len(collisions)}")
if len(collisions):
    print(collisions.to_string())
    for code in collisions.index:
        print(f"\n--- {code} candidates ---")
        print(ourair_iata[ourair_iata["iata_code"] == code][
            ["ident", "name", "municipality", "iso_region", "latitude_deg", "longitude_deg"]
        ].to_string(index=False))