import pytest
import pandas as pd
import requests
from unittest.mock import patch, MagicMock
from ota_monitor.data_loaders.api_loader import load_data_from_api

@patch('requests.get')
def test_load_data_from_api_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'id': '1', 'data': 'test'}
    mock_get.return_value = mock_response
    
    result = load_data_from_api(api_url='http://test.com', api_token='token')
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]['id'] == '1'

@patch('requests.get')
@patch('time.sleep', return_value=None) # Fast retries
def test_load_data_from_api_retry_then_success(mock_sleep, mock_get):
    # First two fail, third succeeds
    mock_fail = MagicMock()
    mock_fail.raise_for_status.side_effect = requests.exceptions.HTTPError("Fail")
    
    mock_success = MagicMock()
    mock_success.status_code = 200
    mock_success.json.return_value = [{'id': '1'}]
    
    mock_get.side_effect = [mock_fail, mock_fail, mock_success]
    
    result = load_data_from_api(api_url='http://test.com')
    
    assert len(result) == 1
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2

@patch('requests.get')
@patch('time.sleep', return_value=None)
def test_load_data_from_api_exhaust_retries(mock_sleep, mock_get):
    mock_fail = MagicMock()
    mock_fail.raise_for_status.side_effect = requests.exceptions.HTTPError("Permanent Fail")
    mock_get.return_value = mock_fail
    
    with pytest.raises(Exception, match="Failed to fetch data after 3 attempts"):
        load_data_from_api(api_url='http://test.com')
    
    assert mock_get.call_count == 3
