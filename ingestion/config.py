import os

# Database connection (uses .pgpass — no password in code)
DB_CONFIG = {
    "dbname": "aviation",
    "user": "kavin_postgres",
    "host": "localhost",
    "port": 5432,
}

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed")

# BTS file for August 2026
BTS_CSV_PATH = os.path.join(DATA_RAW, "bts_aug2026.csv")
AIRPORT_MAPPING_PATH = os.path.join(DATA_PROCESSED, "airport_mapping.csv")

# Weather window (locked in Phase 1)
WEATHER_START = "2025-08-01"
WEATHER_END = "2026-07-31"

# Open-Meteo
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_VARIABLES = "temperature_2m,precipitation,wind_speed_10m,relative_humidity_2m"