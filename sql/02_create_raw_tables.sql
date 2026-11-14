-- ============================================================================
-- File: 02_create_raw_tables.sql
-- Purpose: Create raw.flights, raw.airports, raw.weather
--          Column types and nullability mirror Phase 1 profiling report.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- raw.flights — one row per flight leg from BTS On-Time Performance
-- Source: BTS DL_SelectFields.aspx?gnoyr_VQ=FGJ
-- Grain: one flight leg (aircraft departure from origin to dest on a date)
-- No natural key exists in BTS — surrogate flight_id assigned here.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS raw.flights CASCADE;

CREATE TABLE raw.flights (
    flight_id              SERIAL          PRIMARY KEY,

    -- Time & flight identification
    flight_date            DATE            NOT NULL,
    reporting_airline      VARCHAR(8)      NOT NULL,       -- e.g. 'AA', 'WN'
    flight_number          INTEGER         NOT NULL,

    -- Origin
    origin_airport_id      INTEGER         NOT NULL,
    origin_iata            CHAR(3)         NOT NULL,
    origin_city            VARCHAR(100)    NOT NULL,
    origin_state           CHAR(2)         NOT NULL,

    -- Destination
    dest_airport_id        INTEGER         NOT NULL,
    dest_iata              CHAR(3)         NOT NULL,
    dest_city              VARCHAR(100)    NOT NULL,
    dest_state             CHAR(2)         NOT NULL,

    -- Scheduled / actual departure times (local time, hhmm as string)
    crs_dep_time           CHAR(4)         NOT NULL,
    dep_time               CHAR(4),                       -- null when cancelled
    dep_delay              NUMERIC(8,2),                  -- negative = early
    dep_delay_minutes      NUMERIC(8,2),                  -- early set to 0
    dep_del15              BOOLEAN,                       -- true = dep delay >= 15 min

    -- Scheduled / actual arrival times (local time, hhmm as string)
    crs_arr_time           CHAR(4)         NOT NULL,
    arr_time               CHAR(4),                       -- null when cancelled/diverted
    arr_delay              NUMERIC(8,2),                  -- negative = early; null when cancelled/diverted
    arr_delay_minutes      NUMERIC(8,2),
    arr_del15              BOOLEAN,

    -- Cancellations and diversions
    cancelled              BOOLEAN         NOT NULL DEFAULT FALSE,
    cancellation_code      CHAR(1),                       -- A/B/C/D; null when not cancelled
    diverted               BOOLEAN         NOT NULL DEFAULT FALSE,

    -- Delay causes (carrier-reported, populated ONLY when arr_del15 = TRUE)
    -- NULL means "not applicable" — never impute 0
    carrier_delay          NUMERIC(8,2),
    weather_delay          NUMERIC(8,2),
    nas_delay              NUMERIC(8,2),
    security_delay         NUMERIC(8,2),
    late_aircraft_delay    NUMERIC(8,2),

    -- Flight attributes
    distance               NUMERIC(8,2),
    crs_elapsed_time       NUMERIC(8,2),

    -- Ingestion metadata
    ingested_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_cancellation_code CHECK (
        cancellation_code IS NULL OR cancellation_code IN ('A','B','C','D')
    ),
    CONSTRAINT chk_cancelled_code_consistency CHECK (
        (cancelled = TRUE  AND cancellation_code IS NOT NULL) OR
        (cancelled = FALSE AND cancellation_code IS NULL)
    ),
    CONSTRAINT chk_arr_delay_cancelled CHECK (
        -- Arrival delay must be null when cancelled or diverted
        (cancelled = FALSE AND diverted = FALSE) OR arr_delay IS NULL
    ),
    CONSTRAINT chk_delay_cause_requires_delay CHECK (
        -- Any delay cause populated → arr_del15 must be TRUE
        (carrier_delay IS NULL AND weather_delay IS NULL AND nas_delay IS NULL
         AND security_delay IS NULL AND late_aircraft_delay IS NULL)
        OR arr_del15 = TRUE
    )
);

COMMENT ON TABLE  raw.flights IS
    'One row per flight leg from BTS On-Time Performance. Delay cause fields populated only when arr_del15 = TRUE; null means not applicable, never impute zero.';
COMMENT ON COLUMN raw.flights.cancellation_code IS
    'A=Carrier, B=Weather, C=NAS, D=Security. Null when not cancelled.';
COMMENT ON COLUMN raw.flights.carrier_delay IS
    'Carrier-reported delay minutes. Populated ONLY when arr_del15 = TRUE. Null = not applicable.';


-- ----------------------------------------------------------------------------
-- raw.airports — airport dimension from OurAirports joined to BTS airport IDs
-- Source: data/processed/airport_mapping.csv (bridge) + OurAirports airports.csv
-- Grain: one row per BTS airport
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS raw.airports CASCADE;

CREATE TABLE raw.airports (
    bts_airport_id         INTEGER         PRIMARY KEY,
    iata_code              CHAR(3)         NOT NULL,
    icao_code              VARCHAR(8)      NOT NULL,       -- OurAirports 'ident'
    airport_name           VARCHAR(200),
    city                   VARCHAR(100),
    state                  CHAR(2),                       -- canonical = OurAirports iso_region suffix
    country                CHAR(2)         NOT NULL DEFAULT 'US',
    latitude               NUMERIC(10,7)   NOT NULL,
    longitude              NUMERIC(10,7)   NOT NULL,
    ingested_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  raw.airports IS
    'Airport dimension. bts_airport_id is the DOT ID; icao_code is OurAirports ident; state is canonical iso_region suffix.';
COMMENT ON COLUMN raw.airports.state IS
    'Canonical state from OurAirports iso_region (e.g., NY, CA). BTS state code TT is NOT used here.';


-- ----------------------------------------------------------------------------
-- raw.weather — hourly ERA5 reanalysis per airport
-- Source: Open-Meteo Archive API
-- Grain: one row per (airport, hour)
-- IMPORTANT: This is MODELED REANALYSIS at the airport grid cell,
--            NOT on-site station observation. Correlational only, not causal.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS raw.weather CASCADE;

CREATE TABLE raw.weather (
    airport_id             INTEGER         NOT NULL,       -- BTS AirportID
    weather_hour           TIMESTAMPTZ     NOT NULL,       -- UTC; local hour derived in dbt
    temperature_c          NUMERIC(5,2),
    precipitation_mm       NUMERIC(6,2),
    wind_speed_kmh         NUMERIC(6,2),
    relative_humidity_pct  NUMERIC(5,2),
    ingested_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (airport_id, weather_hour),
    CONSTRAINT fk_weather_airport FOREIGN KEY (airport_id)
        REFERENCES raw.airports(bts_airport_id) ON DELETE RESTRICT
);

COMMENT ON TABLE  raw.weather IS
    'Hourly ERA5 reanalysis weather per airport. MODELED, not station observation. Correlational only.';
COMMENT ON COLUMN raw.weather.weather_hour IS
    'UTC timestamp for the hour. Local-time alignment happens in dbt int_flight_airport_weather.';


-- ----------------------------------------------------------------------------
-- Foreign keys on raw.flights (must come after raw.airports is created)
-- ----------------------------------------------------------------------------
ALTER TABLE raw.flights
    ADD CONSTRAINT fk_flights_origin_airport
        FOREIGN KEY (origin_airport_id) REFERENCES raw.airports(bts_airport_id)
        ON DELETE RESTRICT;

ALTER TABLE raw.flights
    ADD CONSTRAINT fk_flights_dest_airport
        FOREIGN KEY (dest_airport_id) REFERENCES raw.airports(bts_airport_id)
        ON DELETE RESTRICT;


-- Verify: list all tables and columns created
SELECT table_schema, table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'raw'
ORDER BY table_name, ordinal_position;