import pytest
import pandas as pd
import json
import os
from unittest.mock import patch, MagicMock
from ota_monitor.transformers.dynamic_pattern_detector import dynamic_pattern_detector

def test_dynamic_detector_empty_df():
    df = pd.DataFrame()
    result = dynamic_pattern_detector(df)
    assert result.empty
    assert 'pattern_type' in result.columns

def test_dynamic_detector_malformed_json():
    # Record with invalid JSON
    df = pd.DataFrame([{'raw_payload': 'invalid-json'}])
    result = dynamic_pattern_detector(df)
    assert result.empty

@patch('os.listdir')
@patch('importlib.util.spec_from_file_location')
def test_dynamic_detector_plugin_execution(mock_spec, mock_listdir):
    # Mock listdir to show one rule file
    mock_listdir.return_value = ['rule_test.py']
    
    # Mock plugin module and its evaluate_rule function
    mock_module = MagicMock()
    mock_module.evaluate_rule.return_value = [{'pattern_type': 'TEST_PATTERN', 'occurrence_count': 5}]
    
    mock_spec_obj = MagicMock()
    mock_spec_obj.loader.exec_module = lambda m: None
    mock_spec.return_value = mock_spec_obj
    
    with patch('importlib.util.module_from_spec', return_value=mock_module):
        # Sample valid data
        raw_data = {
            'id': '1',
            'contentJson': {
                'requestBody': {
                    'vin': 'V1',
                    'updateTime': '2026-05-11T03:00:00Z',
                    'usageModeName': 'DRIVING'
                }
            }
        }
        df = pd.DataFrame([{'raw_payload': json.dumps(raw_data)}])
        
        result = dynamic_pattern_detector(df)
        
        assert not result.empty
        assert result.iloc[0]['pattern_type'] == 'TEST_PATTERN'
        assert result.iloc[0]['occurrence_count'] == 5

def test_dynamic_detector_aggregation():
    # Test that multiple plugins or multiple results are aggregated correctly
    # We'll use the real plugin directory for this test but mock the loaded data
    raw_data = [
        {
            'id': '1',
            'contentJson': {
                'requestBody': {
                    'vin': 'V1',
                    'updateTime': '2026-05-11T03:00:00Z',
                    'usageModeName': 'DRIVING'
                }
            }
        },
        {
            'id': '2',
            'contentJson': {
                'requestBody': {
                    'vin': 'V1',
                    'updateTime': '2026-05-11T03:15:00Z',
                    'usageModeName': 'DRIVING'
                }
            }
        }
    ]
    df = pd.DataFrame([{'raw_payload': json.dumps(r)} for r in raw_data])
    
    # This will run the actual rule_driving_duration.py plugin
    result = dynamic_pattern_detector(df)
    
    assert not result.empty
    assert 'DRIVING_CRITICAL_10MIN' in result['pattern_type'].values
    assert result[result['pattern_type'] == 'DRIVING_CRITICAL_10MIN']['occurrence_count'].iloc[0] == 1
