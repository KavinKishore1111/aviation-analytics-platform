import sys
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import psycopg2
from io import StringIO
from config import DB_CONFIG, BTS_CSV_PATH

# Column mapping: CSV column → DB column
COLUMN_MAP = {
    "FL_DATE": "flight_date",
    "OP_UNIQUE_CARRIER": "reporting_airline",
    "OP_CARRIER_FL_NUM": "flight_number",
    "ORIGIN_AIRPORT_ID": "origin_airport_id",
    "ORIGIN": "origin_iata",
    "ORIGIN_CITY_NAME": "origin_city",
    "ORIGIN_STATE_ABR": "origin_state",
    "DEST_AIRPORT_ID": "dest_airport_id",
    "DEST": "dest_iata",
    "DEST_CITY_NAME": "dest_city",
    "DEST_STATE_ABR": "dest_state",
    "CRS_DEP_TIME": "crs_dep_time",
    "DEP_TIME": "dep_time",
    "DEP_DELAY": "dep_delay",
    "DEP_DELAY_NEW": "dep_delay_minutes",
    "DEP_DEL15": "dep_del15",
    "CRS_ARR_TIME": "crs_arr_time",
    "ARR_TIME": "arr_time",
    "ARR_DELAY": "arr_delay",
    "ARR_DELAY_NEW": "arr_delay_minutes",
    "ARR_DEL15": "arr_del15",
    "CANCELLED": "cancelled",
    "CANCELLATION_CODE": "cancellation_code",
    "DIVERTED": "diverted",
    "CARRIER_DELAY": "carrier_delay",
    "WEATHER_DELAY": "weather_delay",
    "NAS_DELAY": "nas_delay",
    "SECURITY_DELAY": "security_delay",
    "LATE_AIRCRAFT_DELAY": "late_aircraft_delay",
    
}

def load_bts():
    print(f"Reading {BTS_CSV_PATH}...")
    df = pd.read_csv(BTS_CSV_PATH, dtype=str)
    print(f"Rows: {len(df)}")

    # Rename columns
    df = df.rename(columns=COLUMN_MAP)
    db_cols = [c for c in COLUMN_MAP.values() if c in df.columns]
    df = df[db_cols]

    # Type casts (ELT: type-only, no business logic)
    df["flight_date"] = pd.to_datetime(df["flight_date"], format="%m/%d/%Y %I:%M:%S %p").dt.date
    df["flight_number"] = pd.to_numeric(df["flight_number"], errors="coerce").astype("Int64")
    df["origin_airport_id"] = pd.to_numeric(df["origin_airport_id"], errors="coerce").astype("Int64")
    df["dest_airport_id"] = pd.to_numeric(df["dest_airport_id"], errors="coerce").astype("Int64")

    # Boolean casts: "0.00"/"1.00" → False/True
    for col in ["dep_del15", "arr_del15", "cancelled", "diverted"]:
        df[col] = df[col].map({"0.00": False, "1.00": True, "0": False, "1": True})

    # Numeric casts
    for col in ["dep_delay", "dep_delay_minutes", "arr_delay", "arr_delay_minutes",
            "carrier_delay", "weather_delay", "nas_delay", "security_delay",
            "late_aircraft_delay"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure only DB columns, in order
    df = df[db_cols]

    # Load via COPY FROM (fast)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Truncate for idempotency
    cur.execute("TRUNCATE raw.flights RESTART IDENTITY CASCADE;")

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)

    copy_sql = f"COPY raw.flights ({', '.join(db_cols)}) FROM STDIN WITH CSV NULL '\\N'"
    cur.copy_expert(copy_sql, buffer)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM raw.flights;")
    count = cur.fetchone()[0]
    print(f"Loaded {count} rows into raw.flights")

    cur.close()
    conn.close()

if __name__ == "__main__":
    load_bts()