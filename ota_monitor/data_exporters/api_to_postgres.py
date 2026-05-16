from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import PostgreSQL
from mage_ai.data_preparation.decorators import data_exporter
from pandas import DataFrame
from os import path
import json

@data_exporter
def export_data_to_postgres(df: DataFrame, **kwargs) -> None:
    """
    Exports raw JSON payloads to PostgreSQL raw_api_data table (Req 1.3).
    """
    schema_name = kwargs.get('POSTGRES_SCHEMA', 'public')
    table_name = 'raw_api_data'
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    # Convert the entire dataframe rows into raw_payload JSONB format
    # This ensures we store the raw structure regardless of individual column schemas
    records = df.to_dict(orient='records')
    formatted_df = DataFrame([{'raw_payload': json.dumps(r)} for r in records])

    with PostgreSQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        loader.export(
            formatted_df,
            schema_name,
            table_name,
            index=False,  # Specifies whether to include index in exported table
            if_exists='append',  # Specify resolution policy if table name already exists
        )
