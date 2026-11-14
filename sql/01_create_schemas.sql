-- ============================================================================
-- File: 01_create_schemas.sql
-- Purpose: Create the three-layer schema structure (raw / staging / marts)
-- Run once per database (idempotent — safe to re-run)
-- ============================================================================

-- RAW — landing zone. Exactly as ingested. Never modified after load.
CREATE SCHEMA IF NOT EXISTS raw;

-- STAGING — typed, cleaned, tested views over raw. Populated by dbt staging models.
CREATE SCHEMA IF NOT EXISTS staging;

-- MARTS — business-ready facts, dimensions, analytics marts. Populated by dbt.
CREATE SCHEMA IF NOT EXISTS marts;

-- Verify
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN ('raw', 'staging', 'marts')
ORDER BY schema_name;