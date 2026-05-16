# Architectural Design: Extendable Plugin System for Transformation Logic

**Objective:** Decouple specific business rules (e.g., "DRIVING > 10 mins") from the core Mage.ai data pipeline. Allow analysts and users to add new pattern detection rules by simply adding Python files, without needing to modify the main pipeline execution blocks.

## 1. Directory Structure

We will introduce a dedicated `plugins` directory outside of the core Mage.ai block structure.

```text
ota_monitor/
├── plugins/
│   ├── __init__.py
│   ├── rule_driving_duration.py   <-- Existing logic moved here
│   ├── rule_inactive_anomaly.py   <-- New rule dropped in by user
│   └── rule_voltage_drop.py       <-- New rule dropped in by user
├── transformers/
│   └── dynamic_pattern_detector.py <-- Replaces hardcoded logic
...
```

## 2. Plugin Interface Contract

Every python file placed in the `plugins/` folder must adhere to a specific interface contract. 

It must expose a function named `evaluate_rule(df: DataFrame) -> List[Dict]`.

**Example: `rule_inactive_anomaly.py`**
```python
from pandas import DataFrame

def evaluate_rule(df: DataFrame) -> list:
    """
    Contract:
    Input: DataFrame containing parsed records.
    Output: List of dictionaries: [{'pattern_type': 'NAME', 'occurrence_count': int}]
    """
    stats = []
    # ... business logic to find INACTIVE states > 48 hours ...
    # if found:
    #    stats.append({'pattern_type': 'INACTIVE_WARNING_48H', 'occurrence_count': 5})
    
    return stats
```

## 3. Dynamic Transformer Block (`dynamic_pattern_detector.py`)

The Mage.ai transformer block will be refactored to act as a "Plugin Runner". Instead of containing the regex or duration logic itself, it will:

1.  **Parse Payload:** Extract standard fields from the raw JSON (VIN, timestamp, usageMode).
2.  **Discover Plugins:** Use Python's `os` and `importlib` or `pkgutil` to scan the `ota_monitor/plugins/` directory.
3.  **Load Modules:** Dynamically import any `.py` file that starts with `rule_`.
4.  **Execute:** Pass the standardized DataFrame to each plugin's `evaluate_rule(df)` function.
5.  **Aggregate:** Collect the resulting lists from all plugins, aggregate them into a single DataFrame, and return it to the next Mage.ai block (the upsert/alert block).

## 4. Workflow for Users

To add a new business rule, a user will follow these steps:

1.  Create a new Python file (e.g., `rule_speed_violation.py`).
2.  Implement the `evaluate_rule` function adhering to the contract.
3.  Save the file into the `ota_monitor/plugins/` directory.
4.  **Result:** The next time the `pattern_processing` pipeline runs, it will automatically discover the new file, execute its logic against the data, and start generating alerts for `SPEED_VIOLATION` if detected. No server restart or Mage.ai code modification is required.

## 5. Phase 2 Considerations (Kafka integration)
Because the plugins operate on DataFrames and return standard summary dictionaries, this architecture is perfectly compatible with the Phase 2 Kafka micro-batch approach. The dynamic runner will process Kafka batches identically to API batches.
