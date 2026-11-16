import sys
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import psycopg2
from io import StringIO
from config import DB_CONFIG, AIRPORT_MAPPING_PATH

def load_airports():
    print(f"Reading {AIRPORT_MAPPING_PATH}...")
    df = pd.read_csv(AIRPORT_MAPPING_PATH, dtype=str)
    print(f"Rows: {len(df)}")

    # Map to raw.airports columns
    out = pd.DataFrame({
        "bts_airport_id": pd.to_numeric(df["bts_airport_id"], errors="coerce").astype("Int64"),
        "iata_code": df["bts_iata"].str.strip().str.upper(),
        "icao_code": df["ourairports_ident"].str.strip().str.upper(),
        "airport_name": df["ourairports_city"],  # placeholder; could join OurAirports for name
        "city": df["ourairports_city"],
        "state": df["ourairports_region"].str.extract(r"US-(\w+)")[0],
        "country": "US",
        "latitude": pd.to_numeric(df["lat"], errors="coerce"),
        "longitude": pd.to_numeric(df["lon"], errors="coerce"),
    })

    # Filter to mapped only (all 352 are mapped per Phase 1)
    out = out[out["bts_airport_id"].notna()]

    db_cols = ["bts_airport_id", "iata_code", "icao_code", "airport_name",
               "city", "state", "country", "latitude", "longitude"]

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Must truncate flights first due to FK
    cur.execute("TRUNCATE raw.flights, raw.airports RESTART IDENTITY CASCADE;")

    buffer = StringIO()
    out.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)

    copy_sql = f"COPY raw.airports ({', '.join(db_cols)}) FROM STDIN WITH CSV NULL '\\N'"
    cur.copy_expert(copy_sql, buffer)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM raw.airports;")
    print(f"Loaded {cur.fetchone()[0]} rows into raw.airports")

    cur.close()
    conn.close()

if __name__ == "__main__":
    load_airports()