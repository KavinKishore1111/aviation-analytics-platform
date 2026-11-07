import pandas as pd
import sys
sys.stdout.reconfigure(encoding="utf-8")

bts = pd.read_csv("data/raw/bts_airports_unique.csv", dtype=str)
ourair = pd.read_csv("data/raw/airports.csv", dtype=str, usecols=[
    "ident", "iata_code", "latitude_deg", "longitude_deg", "municipality", "iso_region"
])

# Keep only rows with iata_code in OurAirports (avoid matching nulls)
ourair_valid = ourair.dropna(subset=["iata_code"]).copy()
ourair_valid = ourair_valid.drop_duplicates(subset="iata_code", keep="first")

# Left join
mapping = bts.merge(
    ourair_valid,
    left_on="bts_iata",
    right_on="iata_code",
    how="left",
    suffixes=("", "_ourair")
)


# Mark mapped status
mapping["mapped"] = mapping["ident"].notna()

# Generate unmapped reason
mapping["unmapped_reason"] = ""
unmapped_mask = ~mapping["mapped"]
mapping.loc[unmapped_mask, "unmapped_reason"] = "IATA code not found in OurAirports"

# Rename columns for clarity
mapping = mapping.rename(columns={
    "ident": "ourairports_ident",
    "iata_code": "ourairports_iata",
    "latitude_deg": "lat",
    "longitude_deg": "lon",
    "municipality": "ourairports_city",
    "iso_region": "ourairports_region"
})

# Output
mapping.to_csv("data/processed/airport_mapping.csv", index=False)

# Stats
total = len(mapping)
mapped_count = mapping["mapped"].sum()
print(f"Total BTS airports: {total}")
print(f"Mapped: {mapped_count} ({mapped_count/total*100:.2f}%)")
print(f"Unmapped: {total - mapped_count}")
print("\n=== Unmapped list ===")
print(mapping.loc[unmapped_mask, ["bts_airport_id", "bts_iata", "bts_city", "bts_state", "unmapped_reason"]])



