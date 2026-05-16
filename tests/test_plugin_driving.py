import pytest
import pandas as pd
from ota_monitor.plugins.rule_driving_duration import evaluate_rule

def test_evaluate_rule_empty_df():
    df = pd.DataFrame()
    results = evaluate_rule(df)
    assert results == []

def test_evaluate_rule_no_driving():
    data = [
        {'vin': 'V1', 'updateTime': '2026-05-11T03:00:00Z', 'usageModeName': 'INACTIVE'},
        {'vin': 'V1', 'updateTime': '2026-05-11T03:05:00Z', 'usageModeName': 'CONVENIENCE'}
    ]
    df = pd.DataFrame(data)
    results = evaluate_rule(df)
    assert results == []

def test_evaluate_rule_short_driving():
    # Driving for 2 minutes (less than 3)
    data = [
        {'vin': 'V1', 'updateTime': '2026-05-11T03:00:00Z', 'usageModeName': 'DRIVING'},
        {'vin': 'V1', 'updateTime': '2026-05-11T03:02:00Z', 'usageModeName': 'DRIVING'}
    ]
    df = pd.DataFrame(data)
    results = evaluate_rule(df)
    assert results == []

def test_evaluate_rule_warning_driving():
    # Driving for 5 minutes (between 3 and 10)
    data = [
        {'vin': 'V1', 'updateTime': '2026-05-11T03:00:00Z', 'usageModeName': 'DRIVING'},
        {'vin': 'V1', 'updateTime': '2026-05-11T03:05:00Z', 'usageModeName': 'DRIVING'}
    ]
    df = pd.DataFrame(data)
    results = evaluate_rule(df)
    assert len(results) == 1
    assert results[0]['pattern_type'] == 'DRIVING_WARNING_3MIN'
    assert results[0]['occurrence_count'] == 1

def test_evaluate_rule_critical_driving():
    # Driving for 15 minutes (more than 10)
    data = [
        {'vin': 'V1', 'updateTime': '2026-05-11T03:00:00Z', 'usageModeName': 'DRIVING'},
        {'vin': 'V1', 'updateTime': '2026-05-11T03:15:00Z', 'usageModeName': 'DRIVING'}
    ]
    df = pd.DataFrame(data)
    results = evaluate_rule(df)
    assert len(results) == 1
    assert results[0]['pattern_type'] == 'DRIVING_CRITICAL_10MIN'
    assert results[0]['occurrence_count'] == 1

def test_evaluate_rule_multiple_vins_mixed():
    data = [
        # V1: 15 min driving (Critical)
        {'vin': 'V1', 'updateTime': '2026-05-11T03:00:00Z', 'usageModeName': 'DRIVING'},
        {'vin': 'V1', 'updateTime': '2026-05-11T03:15:00Z', 'usageModeName': 'DRIVING'},
        # V2: 5 min driving (Warning)
        {'vin': 'V2', 'updateTime': '2026-05-11T03:00:00Z', 'usageModeName': 'DRIVING'},
        {'vin': 'V2', 'updateTime': '2026-05-11T03:05:00Z', 'usageModeName': 'DRIVING'},
        # V3: Interrupted driving (No alert if segments < 3min)
        {'vin': 'V3', 'updateTime': '2026-05-11T03:00:00Z', 'usageModeName': 'DRIVING'},
        {'vin': 'V3', 'updateTime': '2026-05-11T03:01:00Z', 'usageModeName': 'INACTIVE'},
        {'vin': 'V3', 'updateTime': '2026-05-11T03:02:00Z', 'usageModeName': 'DRIVING'},
    ]
    df = pd.DataFrame(data)
    results = evaluate_rule(df)
    
    # Expect 1 Critical, 1 Warning
    types = [r['pattern_type'] for r in results]
    assert 'DRIVING_CRITICAL_10MIN' in types
    assert 'DRIVING_WARNING_3MIN' in types
    assert len(results) == 2
