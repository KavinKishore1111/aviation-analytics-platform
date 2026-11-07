import pandas as pd
import sys
sys.stdout.reconfigure(encoding="utf-8")

df = pd.read_csv("data/raw/bts_aug2026.csv", dtype=str)

# Extract origin airports
orig = df[["ORIGIN_AIRPORT_ID", "ORIGIN", "ORIGIN_CITY_NAME", "ORIGIN_STATE_ABR"]].copy()
orig.columns = ["bts_airport_id", "bts_iata", "bts_city", "bts_state"]

# Extract destination airports, rename to match origin column names
dest = df[["DEST_AIRPORT_ID", "DEST", "DEST_CITY_NAME", "DEST_STATE_ABR"]].copy()
dest.columns = ["bts_airport_id", "bts_iata", "bts_city", "bts_state"]

# Concatenate and deduplicate
bts_airports = pd.concat([orig, dest]).drop_duplicates(subset="bts_airport_id")
bts_airports.to_csv("data/bts_airports_unique.csv", index=False)

print("BTS unique airports:", len(bts_airports))
print(bts_airports.head())