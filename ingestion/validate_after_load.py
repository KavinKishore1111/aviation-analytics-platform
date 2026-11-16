import sys
sys.stdout.reconfigure(encoding="utf-8")

import psycopg2
from config import DB_CONFIG

EXPECTED = {
    "raw.flights": 608389,
    "raw.airports": 352,
}

def validate():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("=== Row counts ===")
    for table, expected in EXPECTED.items():
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        actual = cur.fetchone()[0]
        status = "OK" if actual == expected else f"MISMATCH (expected {expected})"
        print(f"{table}: {actual} — {status}")

    cur.execute("SELECT COUNT(*) FROM raw.weather;")
    print(f"raw.weather: {cur.fetchone()[0]} (expected ~3.08M = 352 × 8760)")

    print("\n=== Null checks (must match Phase 1 profiling) ===")
    checks = [
        ("raw.flights", "arr_delay", "null when cancelled/diverted"),
        ("raw.flights", "weather_delay", "null when arr_del15=FALSE"),
        ("raw.flights", "cancellation_code", "null when not cancelled"),
    ]
    for table, col, note in checks:
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL;")
        print(f"{table}.{col}: {cur.fetchone()[0]} nulls ({note})")

    cur.close()
    conn.close()

if __name__ == "__main__":
    validate()