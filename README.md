# OTA Monitor: Text Pattern Monitoring Pipeline

A data pipeline system built with Mage.ai, PostgreSQL, and Grafana for detecting complex text patterns.

## Getting Started

1.  **Environment Setup:**
    ```bash
    cp .env.example .env
    # Edit .env if necessary
    ```

2.  **Start the Stack:**
    ```bash
    docker-compose up -d
    ```

3.  **Access Services:**
    *   **Mage.ai:** [http://localhost:6789](http://localhost:6789)
    *   **PostgreSQL:** `localhost:5433` (as defined in `docker-compose.yml`)

## Project Structure

*   `ota_monitor/`: Mage.ai project directory.
*   `init.sql`: Database initialization script.
*   `SPECIFICATION.md`: System requirements (v1.1).
*   `DIAGRAMS.md`: Architectural and data flow diagrams.
*   `CODE_REVIEW.md`: Expert review and future roadmap.
*   `GRAFANA_GUIDE.md`: How to set up the visualization dashboard.

## Current Status
- [x] Infrastructure Scaffolding (Docker, Postgres, Mage.ai)
- [x] Database Schema Design
- [x] Phase 1: REST API Ingestion (api_ingestion)
- [x] Phase 1: Pattern Detection Logic (pattern_processing)
- [x] Phase 1: Throttled Alerting (email_alerter)
- [x] **Test Automation: 92% Coverage achieved**
- [ ] Phase 2: Kafka Integration (Planned)
