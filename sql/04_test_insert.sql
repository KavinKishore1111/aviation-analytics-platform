-- ============================================================================
-- File: 04_test_insert.sql
-- Purpose: Verify the schema accepts valid data and rejects invalid data.
--          Order matters: airports MUST be inserted before flights and weather
--          because of the foreign key constraints.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Insert all four airports referenced by the test flights and weather
-- ----------------------------------------------------------------------------
INSERT INTO raw.airports
    (bts_airport_id, iata_code, icao_code, airport_name, city, state, latitude, longitude)
VALUES
    (12478, 'JFK', 'KJFK', 'John F Kennedy International Airport',
     'New York', 'NY', 40.639447, -73.779317),
    (12892, 'LAX', 'KLAX', 'Los Angeles International Airport',
     'Los Angeles', 'CA', 33.942501, -118.407997),
    (13930, 'ORD', 'KORD', 'Chicago O''Hare International Airport',
     'Chicago', 'IL', 41.978600, -87.904800),
    (15016, 'STL', 'KSTL', 'St. Louis Lambert International Airport',
     'St. Louis', 'MO', 38.748697, -90.370003);

-- ----------------------------------------------------------------------------
-- 2. Insert one valid on-time flight (JFK → LAX)
-- ----------------------------------------------------------------------------
INSERT INTO raw.flights
    (flight_date, reporting_airline, flight_number,
     origin_airport_id, origin_iata, origin_city, origin_state,
     dest_airport_id, dest_iata, dest_city, dest_state,
     crs_dep_time, dep_time, dep_delay, dep_delay_minutes, dep_del15,
     crs_arr_time, arr_time, arr_delay, arr_delay_minutes, arr_del15,
     cancelled, diverted, cancellation_code, distance, crs_elapsed_time)
VALUES
    ('2026-08-01', 'AA', 1,
     12478, 'JFK', 'New York, NY', 'NY',
     12892, 'LAX', 'Los Angeles, CA', 'CA',
     '0900', '0855', -5.00, 0.00, FALSE,
     '1158', '1137', -21.00, 0.00, FALSE,
     FALSE, FALSE, NULL, 2475, 360);

-- ----------------------------------------------------------------------------
-- 3. Insert one valid cancelled flight (JFK → LAX, code B = Weather)
-- ----------------------------------------------------------------------------
INSERT INTO raw.flights
    (flight_date, reporting_airline, flight_number,
     origin_airport_id, origin_iata, origin_city, origin_state,
     dest_airport_id, dest_iata, dest_city, dest_state,
     crs_dep_time, dep_time, dep_delay, dep_delay_minutes, dep_del15,
     crs_arr_time, arr_time, arr_delay, arr_delay_minutes, arr_del15,
     cancelled, diverted, cancellation_code, distance, crs_elapsed_time)
VALUES
    ('2026-08-01', 'AA', 100,
     12478, 'JFK', 'New York, NY', 'NY',
     12892, 'LAX', 'Los Angeles, CA', 'CA',
     '1200', NULL, NULL, NULL, NULL,
     '1500', NULL, NULL, NULL, NULL,
     TRUE, FALSE, 'B', 2475, 360);

-- ----------------------------------------------------------------------------
-- 4. Insert one delayed flight with cause fields (ORD → STL)
-- ----------------------------------------------------------------------------
INSERT INTO raw.flights
    (flight_date, reporting_airline, flight_number,
     origin_airport_id, origin_iata, origin_city, origin_state,
     dest_airport_id, dest_iata, dest_city, dest_state,
     crs_dep_time, dep_time, dep_delay, dep_delay_minutes, dep_del15,
     crs_arr_time, arr_time, arr_delay, arr_delay_minutes, arr_del15,
     cancelled, diverted,
     carrier_delay, weather_delay, nas_delay, security_delay, late_aircraft_delay,
     distance, crs_elapsed_time)
VALUES
    ('2026-08-01', 'AA', 1004,
     13930, 'ORD', 'Chicago, IL', 'IL',
     15016, 'STL', 'St. Louis, MO', 'MO',
     '2259', '0043', 104.00, 104.00, TRUE,
     '0015', '0142', 87.00, 87.00, TRUE,
     FALSE, FALSE,
     17.00, 0.00, 0.00, 0.00, 70.00,
     258, 90);

-- ----------------------------------------------------------------------------
-- 5. Insert weather for the four airports
-- ----------------------------------------------------------------------------
INSERT INTO raw.weather
    (airport_id, weather_hour, temperature_c, precipitation_mm, wind_speed_kmh, relative_humidity_pct)
VALUES
    (12478, '2026-08-01 13:00:00+00', 22.5, 0.0, 12.0, 78.0),
    (12892, '2026-08-01 19:00:00+00', 28.0, 0.0, 15.5, 45.0),
    (13930, '2026-08-02 03:59:00+00', 18.0, 1.2, 20.0, 85.0),
    (15016, '2026-08-02 06:15:00+00', 20.0, 0.0, 10.0, 70.0);

-- ----------------------------------------------------------------------------
-- Verify counts
-- ----------------------------------------------------------------------------
SELECT 'airports' AS t, COUNT(*) FROM raw.airports
UNION ALL
SELECT 'flights', COUNT(*) FROM raw.flights
UNION ALL
SELECT 'weather', COUNT(*) FROM raw.weather;