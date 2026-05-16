from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import PostgreSQL
from mage_ai.data_preparation.decorators import data_exporter
from pandas import DataFrame
from os import path
import datetime

@data_exporter
def upsert_pattern_summary(df: DataFrame, **kwargs) -> None:
    """
    Upserts aggregated results into pattern_summary (Req 3.1).
    """
    if df.empty:
        return

    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    
    # We use a raw SQL execution for UPSERT logic
    with PostgreSQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        for _, row in df.iterrows():
            pattern_type = row['pattern_type']
            count = row['occurrence_count']
            now = datetime.datetime.now()
            
            sql = f"""
                INSERT INTO pattern_summary (pattern_type, occurrence_count, last_detected_at, updated_at)
                VALUES ('{pattern_type}', {count}, '{now}', '{now}')
                ON CONFLICT (pattern_type) 
                DO UPDATE SET 
                    occurrence_count = pattern_summary.occurrence_count + EXCLUDED.occurrence_count,
                    last_detected_at = EXCLUDED.last_detected_at,
                    updated_at = EXCLUDED.updated_at;
            """
            loader.execute(sql)
