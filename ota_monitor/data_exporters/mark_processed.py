from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import PostgreSQL
from mage_ai.data_preparation.decorators import data_exporter
from pandas import DataFrame
from os import path

@data_exporter
def mark_records_as_processed(df: DataFrame, **kwargs) -> None:
    """
    Updates the processed flag to TRUE for the records just analyzed.
    Input df must contain 'id' from the raw_api_data table.
    """
    if df.empty or 'id' not in df.columns:
        return

    ids = df['id'].dropna().unique().tolist()
    if not ids:
        return

    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    
    id_list = ", ".join(map(str, ids))
    query = f"UPDATE raw_api_data SET processed = TRUE WHERE id IN ({id_list})"

    with PostgreSQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        loader.execute(query)
