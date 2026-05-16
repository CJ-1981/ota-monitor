-- Initial Schema for Text Pattern Monitoring and Alerting Pipeline

-- Phase 1: Raw API Data
CREATE TABLE IF NOT EXISTS raw_api_data (
    id SERIAL PRIMARY KEY,
    raw_payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Phase 2: Raw Kafka Events
CREATE TABLE IF NOT EXISTS raw_kafka_events (
    id SERIAL PRIMARY KEY,
    event_payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated Pattern Results
CREATE TABLE IF NOT EXISTS pattern_summary (
    pattern_type VARCHAR(50) PRIMARY KEY,
    occurrence_count BIGINT DEFAULT 0,
    last_detected_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quarantine for failed records
CREATE TABLE IF NOT EXISTS quarantine_logs (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(50),
    record_id INTEGER,
    error_message TEXT,
    failed_payload JSONB,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_kafka_unprocessed ON raw_kafka_events (processed) WHERE processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_api_ingested_at ON raw_api_data (ingested_at);

-- Alert History for throttling (Req 3.3)
CREATE TABLE IF NOT EXISTS alert_history (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
