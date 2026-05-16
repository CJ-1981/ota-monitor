# System Diagrams: Text Pattern Monitoring Pipeline

This document provides visual representations of the system architecture, data flows, and process sequences.

## 1. System Architecture (Hybrid Phase 1 & 2)

This diagram shows the evolution from REST API ingestion to the Kafka-based stream ingestion while maintaining a consistent transformation and serving layer.

```mermaid
graph TD
    subgraph "Data Sources"
        API[REST API Source]
        Kafka[Kafka Topic]
    end

    subgraph "Ingestion Layer (Phase 1 & 2)"
        Mage_Extract[Mage.ai: REST Loader]
        Kafka_Connect[Kafka Connect Sink]
    end

    subgraph "Storage Layer (PostgreSQL)"
        Raw_API[(raw_api_data)]
        Raw_Kafka[(raw_kafka_events)]
        Summary[(pattern_summary)]
        Quarantine[(quarantine_logs)]
    end

    subgraph "Transformation Layer (Mage.ai)"
        Mage_Transform[Python/Pandas/Regex Engine]
    end

    subgraph "Serving & Alerting"
        Grafana[Grafana Dashboard]
        Email[SMTP: Email Alerts]
    end

    %% Phase 1 Flow
    API --> Mage_Extract
    Mage_Extract --> Raw_API
    Raw_API --> Mage_Transform

    %% Phase 2 Flow
    Kafka --> Kafka_Connect
    Kafka_Connect --> Raw_Kafka
    Raw_Kafka --> Mage_Transform

    %% Common Flow
    Mage_Transform --> Summary
    Mage_Transform -- "Failures" --> Quarantine
    Summary --> Grafana
    Summary -- "Critical Event" --> Email
```

---

## 2. Data Flow Diagram (DFD)

Focusing on the transformation logic and state transitions.

```mermaid
flowchart LR
    Raw[Raw Text Data] --> Parse{Parse JSON}
    Parse -- "Success" --> Regex[Regex Engine]
    Parse -- "Error" --> Log[Quarantine Log]
    
    Regex --> Match{Pattern Detected?}
    Match -- "Yes" --> Flag[Flag Record & Type]
    Match -- "No" --> Skip[Discard/Archive]
    
    Flag --> Agg[Aggregate by Type]
    Agg --> Upsert[Upsert pattern_summary]
    
    Upsert --> Alert{is Critical?}
    Alert -- "Yes (Throttled)" --> EmailNotif[Send Email]
```

---

## 3. Message Sequence Diagram (Alerting Pipeline)

Illustrating the timing and coordination between components.

```mermaid
sequenceDiagram
    participant Source as External Source (API/Kafka)
    participant DB as PostgreSQL
    participant Mage as Mage.ai Pipeline
    participant SMTP as SMTP Server
    participant User as End User (Grafana/Email)

    Source->>DB: Write Raw Data
    Note over Mage: Scheduled Trigger (Cron)
    Mage->>DB: Fetch Unprocessed Records
    DB-->>Mage: Return Batch
    
    loop Intra-record Detection
        Mage->>Mage: Apply Regex Patterns
    end

    alt Pattern Detected
        Mage->>DB: Upsert pattern_summary
        DB-->>User: Refresh Dashboard (Grafana)
        
        opt is Critical & Time > 5m since last alert
            Mage->>SMTP: Trigger Summary Email
            SMTP-->>User: Receive Alert
        end
    else Parsing Failure
        Mage->>DB: Write to quarantine_logs
    end

    Mage->>DB: Update 'processed' status (Phase 2)
```
