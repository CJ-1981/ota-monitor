from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import PostgreSQL
from mage_ai.data_preparation.decorators import data_exporter
from pandas import DataFrame
from os import path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

@data_exporter
def trigger_email_alerts(df: DataFrame, **kwargs) -> None:
    """
    Sends summary email for Critical patterns, throttled to 5 min (Req 3.3).
    """
    if df.empty:
        return

    # Check if we have any CRITICAL patterns in the current results
    critical_df = df[df['pattern_type'].str.contains('CRITICAL', na=False)]
    if critical_df.empty:
        return

    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config = ConfigFileLoader(config_path, config_profile)

    with PostgreSQL.with_config(config) as loader:
        # 1. Throttling Check: Get last alert time
        last_alert_query = "SELECT sent_at FROM alert_history ORDER BY sent_at DESC LIMIT 1"
        last_alert_result = loader.load(last_alert_query)
        
        should_send = True
        if not last_alert_result.empty:
            last_sent = last_alert_result.iloc[0]['sent_at']
            if (datetime.datetime.now(datetime.timezone.utc) - last_sent).total_seconds() < 300:
                print("Alert throttled. Last email sent less than 5 minutes ago.")
                should_send = False

        if should_send:
            # 2. Compose Email
            smtp_server = config.get('SMTP_SERVER')
            smtp_port = config.get('SMTP_PORT')
            smtp_user = config.get('SMTP_EMAIL')
            smtp_pass = config.get('SMTP_PASSWORD')
            recipient = kwargs.get('alert_recipient', smtp_user)

            if not all([smtp_server, smtp_port, smtp_user, smtp_pass]):
                print("SMTP credentials missing. Skipping email.")
                return

            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = f"CRITICAL: Text Pattern Alert - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

            body = "The following critical patterns were detected in the latest run:\n\n"
            body += critical_df.to_string(index=False)
            body += "\n\nVisit Grafana for details."
            
            msg.attach(MIMEText(body, 'plain'))

            try:
                server = smtplib.SMTP(smtp_server, int(smtp_port))
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                server.quit()
                print(f"Alert email sent to {recipient}")

                # 3. Log success to alert_history
                loader.execute("INSERT INTO alert_history (alert_type) VALUES ('CRITICAL_SUMMARY')")
            except Exception as e:
                print(f"Failed to send email: {e}")
