# Test Automation Plan: OTA Pattern Monitoring Pipeline

**Version:** 1.0
**Target Coverage:** > 90% (Statement & Branch)
**Author:** Test Automation Architecture Team

## 1. Executive Summary
This document outlines the test automation strategy for the OTA Pattern Monitoring Pipeline (Phase 1). To achieve >90% test coverage and ensure high reliability of the dynamic plugin architecture, we will employ a **Test Pyramid** approach: a massive base of Unit Tests for business logic (plugins), supported by robust Integration Tests for data I/O, and validated by End-to-End (E2E) and Performance tests.

## 2. Test Pyramid & Scope

### 2.1. Unit Testing (Target: 95% Coverage)
**Focus:** Individual Mage blocks (transformers), dynamic plugin loaders, and specific business rule plugins.
**Tools:** `pytest`, `unittest.mock`, `pandas.testing`
*   **Plugins (`plugins/rule_*.py`):** 
    *   *Strategy:* Parameterized tests feeding various DataFrame edge cases (empty DFs, missing fields, malformed JSON, out-of-order timestamps, cross-batch state boundaries) directly into the `evaluate_rule()` functions.
    *   *Mocking:* None required (pure functions).
*   **Dynamic Loader (`dynamic_pattern_detector.py`):**
    *   *Strategy:* Mock the `os.listdir` and `importlib` to simulate folders with valid, invalid, and malformed plugin files to ensure the runner doesn't crash on bad user input.
*   **Mage Block Tests:**
    *   *Strategy:* Utilize Mage.ai's built-in `@test` decorators to assert output types and schemas locally.

### 2.2. Integration Testing (Target: 85% Coverage)
**Focus:** Component interactions, primarily Mage blocks reading from/writing to PostgreSQL, and API loading.
**Tools:** `pytest`, `testcontainers` (for isolated ephemeral Postgres databases), `responses` or `WireMock` (for HTTP API mocking).
*   **Database Exporters (`api_to_postgres.py`, `summary_upsert.py`):**
    *   *Strategy:* Spin up a temporary PostgreSQL container via `testcontainers`. Execute the exporter blocks and assert the data is correctly written/upserted into the test database.
*   **Database Loaders (`read_raw_data.py`):**
    *   *Strategy:* Pre-seed the test database, run the loader, and assert the resulting DataFrame matches expectations.
*   **API Loader (`api_loader.py`):**
    *   *Strategy:* Mock the external REST API to return 200 (Success), 500/Timeout (triggering the retry backoff), and ultimate failure (testing the pipeline halt).

### 2.3. End-to-End (E2E) Testing (Target: Critical Paths)
**Focus:** The entire pipeline execution from source to email alert.
**Tools:** Mage.ai CLI triggers, Local Docker Compose stack, `MailHog` or `smtp4dev` (for catching emails).
*   **Scenario 1: Happy Path / Critical Alert:**
    *   Inject a payload via mocked API containing a >10 min "DRIVING" sequence. Trigger pipeline run. Assert Postgres `pattern_summary` is updated and `MailHog` catches the "CRITICAL" email.
*   **Scenario 2: Alert Throttling:**
    *   Inject two critical payloads 1 minute apart. Trigger pipelines. Assert only *one* email is caught by the mock SMTP server and `alert_history` reflects the throttle.

### 2.4. Performance & Load Testing
**Focus:** Validating Req 5.1 (10k records < 5 mins) and Req 5.4 (300k baseline).
**Tools:** `Locust` (for API load simulation) or custom Python data generators.
*   **Data Generation:** Create a script to generate 300,000 synthetic JSON payloads.
*   **Benchmark:** Execute the `api_ingestion` and `pattern_processing` pipelines using the local executor. Profile memory usage and execution time. Ensure Pandas transformations within the dynamic loader scale linearly.

## 3. Toolchain & Environment
*   **Framework:** `pytest` (Standard for Python data engineering).
*   **Coverage Reporting:** `pytest-cov` (Fails the CI build if coverage drops below 90%).
*   **Mocking:** `unittest.mock` (Python standard), `responses` (for HTTP).
*   **Ephemeral DB:** `testcontainers-python` (Spins up a Docker Postgres instance per test run to prevent state leakage).
*   **Mock SMTP:** `MailHog` (Added to a `docker-compose.test.yml` to trap outbound emails).

## 4. Implementation Steps (Roadmap)

1.  **Phase A: Foundation & Unit Tests (Days 1-2)**
    *   Install `pytest` and `pytest-cov`.
    *   Write exhaustive unit tests for `rule_driving_duration.py` handling all time-series edge cases.
    *   Implement tests for the dynamic plugin loader ensuring bad plugins are caught and skipped gracefully.
2.  **Phase B: Integration Environment (Days 3-4)**
    *   Set up `testcontainers` for PostgreSQL.
    *   Write tests for `api_to_postgres` and `summary_upsert`, asserting SQL constraints (like UPSERT conflict resolution) work correctly.
3.  **Phase C: API & Alert Mocking (Day 5)**
    *   Implement API retry logic tests using `responses`.
    *   Set up `MailHog` and test the 5-minute throttling logic in `email_alerter.py`.
4.  **Phase D: CI/CD Pipeline Integration (Day 6)**
    *   Create a GitHub Action / GitLab CI script to run `pytest --cov=. --cov-fail-under=90` on every pull request.

## 5. Risk Mitigation for Dynamic Plugins
Because users can add arbitrary Python files to the `plugins/` directory:
*   **Automated Plugin Validation:** The CI/CD pipeline MUST automatically discover and run standard linting (`flake8`) and a generic DataFrame shape test against *any* new file added to the `plugins/` folder to ensure it won't crash the production pipeline.