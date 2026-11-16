import sys
sys.stdout.reconfigure(encoding="utf-8")

import time
import requests
import psycopg2
from io import StringIO
from config import (DB_CONFIG, OPEN_METEO_URL, WEATHER_VARIABLES,
                    WEATHER_START, WEATHER_END)


def fetch_airport_weather(lat, lon, max_retries=4):
    """
    Fetch one airport's full weather window.
    Retries on connection/timeout errors with exponential backoff.
    Raises the last exception if all retries fail.
    """
    params = {
        "latitude": float(lat),
        "longitude": float(lon),
        "start_date": WEATHER_START,
        "end_date": WEATHER_END,
        "hourly": WEATHER_VARIABLES,
        "timezone": "UTC",
    }
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(OPEN_METEO_URL, params=params, timeout=180)
            r.raise_for_status()
            return r.json()["hourly"]
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError) as e:
            if attempt == max_retries:
                raise
            wait = 2 ** attempt  # 2, 4, 8 seconds
            print(f"    retry {attempt}/{max_retries} after {wait}s: {e}")
            time.sleep(wait)


def load_weather():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT bts_airport_id, latitude, longitude FROM raw.airports ORDER BY bts_airport_id;")
    airports = cur.fetchall()
    print(f"Fetching weather for {len(airports)} airports...")

    cur.execute("TRUNCATE raw.weather;")

    all_rows = []
    failed = []

    for i, (airport_id, lat, lon) in enumerate(airports, 1):
        try:
            h = fetch_airport_weather(lat, lon)
            n = len(h["time"])
            for j in range(n):
                all_rows.append((
                    airport_id,
                    h["time"][j],
                    h["temperature_2m"][j],
                    h["precipitation"][j],
                    h["wind_speed_10m"][j],
                    h["relative_humidity_2m"][j],
                ))
            if i % 25 == 0:
                print(f"  {i}/{len(airports)} airports, {len(all_rows)} rows so far")
        except Exception as e:
            failed.append((airport_id, str(e)))
            print(f"  FAILED airport {airport_id} after retries: {e}")

        time.sleep(0.5)  # gentle rate limit

    print(f"\nFetched {len(all_rows)} rows from {len(airports) - len(failed)}/{len(airports)} airports")

    if failed:
        print(f"\n{len(failed)} airports still failed:")
        for aid, err in failed:
            print(f"  {aid}: {err}")
        print("Re-run this script to retry — it truncates and reloads everything, so it's idempotent.")

    # Bulk insert
    buffer = StringIO()
    for row in all_rows:
        buffer.write("\t".join("\\N" if v is None else str(v) for v in row) + "\n")
    buffer.seek(0)

    cur.copy_expert(
        "COPY raw.weather (airport_id, weather_hour, temperature_c, precipitation_mm, wind_speed_kmh, relative_humidity_pct) "
        "FROM STDIN WITH (FORMAT text, NULL '\\N')",
        buffer
    )
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM raw.weather;")
    total = cur.fetchone()[0]
    print(f"\nLoaded {total} rows into raw.weather")

    if failed:
        print(f"Still missing {len(failed)} airports — re-run to retry.")
    else:
        print("All airports loaded successfully.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    load_weather()