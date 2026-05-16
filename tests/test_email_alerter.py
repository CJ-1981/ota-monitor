import pytest
import pandas as pd
import datetime
from unittest.mock import patch, MagicMock
from ota_monitor.data_exporters.email_alerter import trigger_email_alerts

@patch('smtplib.SMTP')
@patch('ota_monitor.data_exporters.email_alerter.PostgreSQL')
@patch('ota_monitor.data_exporters.email_alerter.ConfigFileLoader')
def test_email_alerter_throttled(mock_config_loader, mock_postgres, mock_smtp):
    # Mock data with critical pattern
    df = pd.DataFrame([{'pattern_type': 'DRIVING_CRITICAL_10MIN', 'occurrence_count': 1}])
    
    # Mock last alert to be 1 minute ago (should throttle)
    mock_db = MagicMock()
    mock_postgres.with_config.return_value.__enter__.return_value = mock_db
    
    last_sent = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
    mock_db.load.return_value = pd.DataFrame([{'sent_at': last_sent}])
    
    trigger_email_alerts(df)
    
    # Assert SMTP was NOT called
    assert not mock_smtp.called

@patch('smtplib.SMTP')
@patch('ota_monitor.data_exporters.email_alerter.PostgreSQL')
@patch('ota_monitor.data_exporters.email_alerter.ConfigFileLoader')
def test_email_alerter_sends(mock_config_loader, mock_postgres, mock_smtp):
    df = pd.DataFrame([{'pattern_type': 'DRIVING_CRITICAL_10MIN', 'occurrence_count': 1}])
    
    mock_db = MagicMock()
    mock_postgres.with_config.return_value.__enter__.return_value = mock_db
    
    # Mock config
    mock_config = MagicMock()
    mock_config.get.side_effect = lambda k: {
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SMTP_EMAIL': 'test@test.com',
        'SMTP_PASSWORD': 'pass'
    }.get(k)
    mock_config_loader.return_value = mock_config
    
    # Mock last alert to be 10 minutes ago (should send)
    last_sent = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
    mock_db.load.return_value = pd.DataFrame([{'sent_at': last_sent}])
    
    trigger_email_alerts(df)
    
    # Assert SMTP WAS called
    assert mock_smtp.called
    assert mock_db.execute.called # Check that it logged the alert
