# Grafana Visualization Guide: OTA Pattern Monitoring

This guide explains how to connect Grafana to your PostgreSQL database and set up the monitoring dashboard as specified in **Req 3.2**.

## 1. Connecting the Data Source

1.  **Login to Grafana:** [http://localhost:3000](http://localhost:3000) (if you add Grafana to your stack) or your existing instance.
2.  **Add Data Source:**
    *   Navigate to **Connections** -> **Data Sources** -> **Add data source**.
    *   Select **PostgreSQL**.
3.  **Connection Settings:**
    *   **Host:** `localhost:5433` (if Grafana is outside Docker) or `db:5432` (if inside the same network).
    *   **Database:** `ota_db`
    *   **User:** `mageuser`
    *   **Password:** `magepass`
    *   **TLS/SSL Mode:** `disable` (for local development).
4.  **Save & Test:** Ensure the green "Database Connection OK" message appears.

---

## 2. Recommended Dashboard Panels

Create a new dashboard and add the following panels:

### A. Total Critical Detections (Stat Panel)
*   **Goal:** Immediate visibility of critical alerts.
*   **SQL Query:**
    ```sql
    SELECT 
      occurrence_count 
    FROM pattern_summary 
    WHERE pattern_type = 'DRIVING_CRITICAL_10MIN';
    ```
*   **Thresholds:** Set "Red" if value > 0.

### B. Pattern Distribution (Pie Chart / Bar Gauge)
*   **Goal:** See the breakdown of Warnings vs. Criticals.
*   **SQL Query:**
    ```sql
    SELECT 
      pattern_type as metric,
      occurrence_count as value
    FROM pattern_summary;
    ```

### C. Detection Timeline (Time Series)
*   **Goal:** Track when patterns occur over time.
*   **SQL Query:**
    ```sql
    SELECT
      last_detected_at AS "time",
      pattern_type AS metric,
      occurrence_count AS value
    FROM pattern_summary
    ORDER BY 1;
    ```

### D. Recent Quarantine Logs (Table)
*   **Goal:** Identify if the pipeline is failing to parse certain records (Req 2.4).
*   **SQL Query:**
    ```sql
    SELECT 
      occurred_at as time,
      error_message,
      record_id
    FROM quarantine_logs
    ORDER BY occurred_at DESC
    LIMIT 10;
    ```

---

## 3. Refresh Rate Configuration
To ensure the dashboard reflects the updated data as soon as Mage.ai finishes a run (**Req 3.2**):
1.  In Dashboard Settings, set the **Auto-refresh** interval to `5s` or `10s`.
2.  Grafana will now automatically poll the `pattern_summary` table and refresh the visuals.

## 4. (Optional) Adding Grafana to Docker
If you want to manage Grafana via your `docker-compose.yml`, add this block:
```yaml
  grafana:
    image: grafana/grafana-oss:latest
    ports:
      - 3000:3000
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - ota_network
```
