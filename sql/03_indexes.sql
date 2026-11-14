-- ============================================================================
-- File: 03_indexes.sql
-- Purpose: Indexes on join and filter columns. Each index has a reason.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- raw.flights indexes
-- ----------------------------------------------------------------------------

-- Month-by-month incremental loading in dbt: WHERE flight_date BETWEEN ...
CREATE INDEX idx_flights_flight_date
    ON raw.flights (flight_date);

-- Airline-level analytics: GROUP BY reporting_airline
CREATE INDEX idx_flights_airline
    ON raw.flights (reporting_airline);

-- Origin airport analytics: WHERE origin_airport_id = ...
CREATE INDEX idx_flights_origin_airport
    ON raw.flights (origin_airport_id);

-- Destination airport analytics
CREATE INDEX idx_flights_dest_airport
    ON raw.flights (dest_airport_id);

-- On-time KPI filter: WHERE arr_del15 = FALSE
-- Partial index — cheaper than a full column index since most flights are on-time
CREATE INDEX idx_flights_arr_del15_true
    ON raw.flights (flight_date) WHERE arr_del15 = TRUE;

-- Cancellation filter
CREATE INDEX idx_flights_cancelled
    ON raw.flights (flight_date) WHERE cancelled = TRUE;

-- Composite route index for route-level analytics
CREATE INDEX idx_flights_route
    ON raw.flights (origin_airport_id, dest_airport_id);

-- ----------------------------------------------------------------------------
-- raw.airports indexes
-- ----------------------------------------------------------------------------
-- PK on bts_airport_id already indexed. Add IATA index for joins on IATA.
CREATE INDEX idx_airports_iata
    ON raw.airports (iata_code);

CREATE INDEX idx_airports_state
    ON raw.airports (state);

-- ----------------------------------------------------------------------------
-- raw.weather indexes
-- ----------------------------------------------------------------------------
-- PK on (airport_id, weather_hour) already indexed. Add hour-only index for
-- time-series queries (e.g., "all weather from 2026-08").
CREATE INDEX idx_weather_hour
    ON raw.weather (weather_hour);


-- Verify: list all indexes on the raw schema
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'raw'
ORDER BY tablename, indexname;