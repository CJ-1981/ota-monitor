# User Manual: Text Pattern Monitoring Pipeline

This guide explains how to configure, start, and operate the Phase 1 Text Pattern Monitoring Pipeline.

## 1. Prerequisites
*   Docker and Docker Compose installed on your local machine.
*   An SMTP account (e.g., Gmail with an App Password) for sending email alerts.
*   Basic understanding of REST API endpoints.

## 2. Initial Setup

1.  **Clone the Repository:** Ensure you are in the project root directory.
2.  **Environment Configuration:**
    *   Copy the example environment file: `cp .env.example .env`
    *   Open `.env` and fill in your specific details. 
    *   **Crucially**, update the SMTP variables to enable email alerting:
        ```env
        SMTP_EMAIL=your-email@gmail.com
        SMTP_PASSWORD=your-app-password
        SMTP_SERVER=smtp.gmail.com
        SMTP_PORT=587
        ```

## 3. Starting the Services

Run the following command to start the Mage.ai server and the PostgreSQL database in the background:
```bash
docker-compose up -d
```

To verify the services are running:
```bash
docker-compose ps
```

## 4. Accessing the Application

*   **Mage.ai UI:** Open your web browser and navigate to [http://localhost:6789](http://localhost:6789).
*   **PostgreSQL DB:** The database is exposed on `localhost:5433`. You can connect using tools like DBeaver, pgAdmin, or `psql` using the credentials in your `.env` file (Default User: `mageuser`, Password: `magepass`, DB: `ota_db`).

## 5. Operating the Pipelines

In the Mage.ai UI, you will see two main pipelines:

### A. `api_ingestion` (Extract & Load)
This pipeline fetches data from your source API and saves the raw JSON payloads to the database.
1.  Click on `api_ingestion`.
2.  **Configure API Details:** Open the `api_loader` block. Update the `url` and `headers` variables inside the code or via Mage's variable settings to point to your actual data source.
3.  **Run Pipeline:** Click the "Run pipeline now" button at the top to manually execute the extraction.

### B. `pattern_processing` (Transform & Alert)
This pipeline reads the raw data, applies the "DRIVING" duration logic, aggregates the results, and sends email alerts if critical thresholds are met.
1.  Click on `pattern_processing`.
2.  **Run Pipeline:** Click "Run pipeline now". 
3.  **Check Alerts:** If a vehicle has been in the "DRIVING" state for > 10 minutes, the `email_alerter` block will trigger an email. Subsequent emails will be throttled to a maximum of 1 per 5 minutes.

## 6. Automating the Workflow (Scheduling)

To run these continuously:
1.  Go to the **Triggers** tab on the left sidebar in Mage.ai.
2.  Create a new Schedule Trigger for `api_ingestion` (e.g., every 5 minutes).
3.  Create a second Schedule Trigger for `pattern_processing` (e.g., every 5 minutes, ideally offset from ingestion).

## 7. Troubleshooting
*   **Database connection failed:** Ensure `docker-compose` is running and the credentials match `.env`.
*   **Emails not sending:** Verify your SMTP App Password. If using Gmail, standard passwords often block programmatic access; you must generate an App Password.
*   **Checking Logs:** You can view the logs for any failed pipeline run directly within the Mage.ai UI under the "Pipeline runs" tab.
