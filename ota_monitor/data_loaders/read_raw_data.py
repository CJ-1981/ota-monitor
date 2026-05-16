from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import PostgreSQL
from mage_ai.data_preparation.decorators import data_loader, test
from pandas import DataFrame
from os import path

@data_loader
def load_raw_data_for_transformation(*args, **kwargs):
    """
    Reads only unprocessed raw payloads from PostgreSQL for pattern detection.
    """
    query = 'SELECT id, raw_payload FROM raw_api_data WHERE processed = FALSE'
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    with PostgreSQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        return loader.load(query)

@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
