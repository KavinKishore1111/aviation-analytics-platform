import requests

r = requests.get("https://archive-api.open-meteo.com/v1/archive", params={
    "latitude": 41.9786,
    "longitude": -87.9048,
    "start_date": "2025-08-01",
    "end_date": "2026-07-31",
    "hourly": "temperature_2m,precipitation,wind_speed_10m,relative_humidity_2m",
    "timezone": "America/Chicago",
}, timeout=120)

r.raise_for_status()
h = r.json()["hourly"]
print("rows:", len(h["time"]))
print("first:", h["time"][0])
print("last:", h["time"][-1])
print("nulls:", {k: sum(v is None for v in h[k]) for k in h if k != "time"})