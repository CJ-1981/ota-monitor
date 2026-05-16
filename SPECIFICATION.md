# System Specification: Text Pattern Monitoring and Alerting Pipeline

**Document Version:** 1.1
**Date:** 2023-10-26 (Updated: 2026-05-16)
**Author:** Data Architecture Team / Gemini CLI
**Format:** Easy Approach to Requirements Syntax (EARS)

## 1. Introduction
This document specifies the requirements for a data pipeline system designed to ingest text data, detect complex patterns using sequential conditions, update a monitoring dashboard, and trigger email alerts. The system will be implemented in two phases: Phase 1 focuses on REST API ingestion with batch processing; Phase 2 evolves the architecture to utilize a SQL database and Kafka stream ingestion.

**Environment Note:** Initial development and deployment will be targeted for a local self-managed environment (Docker/Localhost).

## 2. Acronyms and Definitions
*   **EARS:** Easy Approach to Requirements Syntax
*   **ELT:** Extract, Load, Transform
*   **CDC:** Change Data Capture
*   **Pipeline:** A scheduled workflow in Mage.ai consisting of distinct executable blocks.
*   **Intra-record:** Pattern detection logic that operates strictly within the scope of a single text record/payload.

---

## 3. Phase 1: REST API Source (Short-Term)

### 3.1 Data Ingestion (Extract & Load)
*   **Req 1.1 (Ubiquitous):** The system shall fetch data from the specified REST API endpoint according to a configured cron schedule.
*   **Req 1.2 (Ubiquitous):** The system shall authenticate with the REST API using credentials stored in Mage.ai's secure environment variables.
*   **Req 1.3 (State-driven):** If the REST API returns data successfully, the system shall load the raw JSON payload into the `raw_api_data` table in the PostgreSQL database.
*   **Req 1.4 (State-driven):** If the REST API returns an HTTP error code or times out, the system shall retry the request up to 3 times with a 60-second exponential backoff interval.
*   **Req 1.5 (Unwanted Behavior):** If the REST API request fails after 3 retries, the system shall halt the pipeline execution and log a connection error.

### 3.2 Data Transformation (Pattern Detection)
*   **Req 2.1 (Ubiquitous):** The system shall execute Python (Pandas/Regex) code to evaluate complex, sequential text conditions **within each individual record (intra-record)**.
*   **Req 2.2 (Event-driven):** When a record meets the defined complex text pattern criteria, the system shall flag the record with a `pattern_detected = TRUE` boolean column and a `pattern_type` categorical column.
*   **Req 2.3 (Ubiquitous):** The system shall calculate the total occurrences of each `pattern_type` for the current execution batch.
*   **Req 2.4 (Unwanted Behavior):** If a text record causes a parsing or Regex error during transformation, the system shall skip the record, log the error to a `quarantine_logs` table with the record ID, and continue processing the remaining batch.

### 3.3 Data Serving (Dashboard & Alerting)
*   **Req 3.1 (State-driven):** If the transformation successfully identifies one or more records matching the critical pattern criteria, the system shall upsert the aggregated results into the `pattern_summary` table in PostgreSQL.
*   **Req 3.2 (Event-driven):** When new critical pattern data is written to the PostgreSQL database, the Grafana dashboard shall automatically refresh to reflect the updated occurrence counts.
*   **Req 3.3 (Event-driven):** When records are flagged with a `pattern_type` of "Critical", the system shall trigger a summary email notification to the distribution list, **throttled to a minimum interval of 5 minutes** to prevent alert fatigue.
*   **Req 3.4 (Optional Feature):** If the pipeline execution completes with zero critical patterns detected, the system may send an "All Clear" status email.

---

## 4. Phase 2: SQL Database & Kafka Source (Long-Term)

### 4.1 Data Ingestion (Kafka to Postgres)
*   **Req 4.1 (Ubiquitous):** A Kafka Connect Sink connector shall continuously consume events from the specified Kafka topic and write them to the `raw_kafka_events` table in PostgreSQL.
*   **Req 4.2 (Ubiquitous):** The incoming Kafka events shall include a `processed` boolean column defaulting to `FALSE`.
*   **Req 4.3 (Unwanted Behavior):** If the Kafka Connect Sink encounters a poison pill (un-parsable message), it shall route the message to a Dead Letter Queue (DLQ) rather than halting the ingestion pipeline.

### 4.2 Data Transformation (Micro-Batch Processing)
*   **Req 4.4 (Ubiquitous):** The system shall execute the Mage.ai pipeline on a scheduled basis to process unhandled Kafka events.
*   **Req 4.5 (Ubiquitous):** The system shall extract records from the `raw_kafka_events` table where `processed = FALSE`.
*   **Req 4.6 (State-driven):** If the Python transformation logic successfully evaluates a batch of unprocessed records, the system shall update the `processed` column to `TRUE` for those specific records in the `raw_kafka_events` table.
*   **Req 4.7 (Unwanted Behavior):** If the Mage.ai pipeline fails midway through a batch, the system shall NOT update the `processed` column to `TRUE` for the unprocessed records, ensuring they are picked up in the next scheduled run.

### 4.3 Data Serving (Dashboard & Alerting continuity)
*   **Req 4.8 (Ubiquitous):** The system shall utilize the exact same Python transformation logic (code block) for pattern detection as defined in Phase 1 (Req 2.1 - 2.3).
*   **Req 4.9 (Ubiquitous):** The Grafana dashboard and email alerting mechanisms shall remain functionally identical to Phase 1, reading from the same `pattern_summary` PostgreSQL table.

---

## 5. Non-Functional Requirements

*   **Req 5.1 (Ubiquitous):** The Mage.ai pipeline execution shall complete within 5 minutes for batches up to 10,000 records.
*   **Req 5.2 (Ubiquitous):** The system shall store all API credentials, database passwords, and SMTP keys as Mage.ai environment variables or external secrets.
*   **Req 5.3 (Ubiquitous):** The system shall log execution metrics (start/end time, record counts, errors) for every pipeline run.
*   **Req 5.4 (Scale):** The system shall support an initial baseline ingestion of **300,000 records** and a steady-state daily volume of **2,000 records**.
*   **Req 5.5 (Maintenance):** The system shall implement a data retention policy to prune or archive raw data from `raw_api_data` and `raw_kafka_events` after 30 days. No long-term audit storage of raw data is required.
