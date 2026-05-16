import pytest
import pandas as pd
import json
from unittest.mock import patch, MagicMock
from ota_monitor.data_exporters.api_to_postgres import export_data_to_postgres
from ota_monitor.data_exporters.summary_upsert import upsert_pattern_summary
from ota_monitor.data_loaders.read_raw_data import load_raw_data_for_transformation
from ota_monitor.data_exporters.mark_processed import mark_records_as_processed

# ... (other tests)

@patch('ota_monitor.data_exporters.mark_processed.PostgreSQL')
@patch('ota_monitor.data_exporters.mark_processed.ConfigFileLoader')
def test_mark_processed(mock_config_loader, mock_postgres):
    df = pd.DataFrame([{'id': 1}, {'id': 2}])
    mock_db = MagicMock()
    mock_postgres.with_config.return_value.__enter__.return_value = mock_db
    
    mark_records_as_processed(df)
    
    # Verify execute was called with correct UPDATE SQL
    assert mock_db.execute.called
    assert "UPDATE raw_api_data SET processed = TRUE" in mock_db.execute.call_args[0][0]
    assert "WHERE id IN (1, 2)" in mock_db.execute.call_args[0][0]

@patch('ota_monitor.data_exporters.api_to_postgres.PostgreSQL')
@patch('ota_monitor.data_exporters.api_to_postgres.ConfigFileLoader')
def test_api_to_postgres(mock_config_loader, mock_postgres):
    df = pd.DataFrame([{'id': '1', 'val': 'test'}])
    mock_db = MagicMock()
    mock_postgres.with_config.return_value.__enter__.return_value = mock_db
    
    export_data_to_postgres(df)
    
    # Verify export was called
    assert mock_db.export.called
    # Check if data was converted to JSON string correctly
    exported_df = mock_db.export.call_args[0][0]
    assert 'raw_payload' in exported_df.columns
    assert isinstance(exported_df.iloc[0]['raw_payload'], str)

@patch('ota_monitor.data_exporters.summary_upsert.PostgreSQL')
@patch('ota_monitor.data_exporters.summary_upsert.ConfigFileLoader')
def test_summary_upsert(mock_config_loader, mock_postgres):
    df = pd.DataFrame([{'pattern_type': 'TEST', 'occurrence_count': 1}])
    mock_db = MagicMock()
    mock_postgres.with_config.return_value.__enter__.return_value = mock_db
    
    upsert_pattern_summary(df)
    
    # Verify execute was called for the SQL UPSERT
    assert mock_db.execute.called
    assert "ON CONFLICT (pattern_type)" in mock_db.execute.call_args[0][0]

@patch('ota_monitor.data_loaders.read_raw_data.PostgreSQL')
@patch('ota_monitor.data_loaders.read_raw_data.ConfigFileLoader')
def test_read_raw_data(mock_config_loader, mock_postgres):
    mock_db = MagicMock()
    mock_postgres.with_config.return_value.__enter__.return_value = mock_db
    mock_db.load.return_value = pd.DataFrame([{'raw_payload': '{}'}])
    
    result = load_raw_data_for_transformation()
    
    assert len(result) == 1
    assert mock_db.load.called
