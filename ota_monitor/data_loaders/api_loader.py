from mage_ai.io.http import HTTPClient
from mage_ai.io.config import ConfigKey, ConfigValues
from mage_ai.data_preparation.decorators import data_loader, test
import pandas as pd
import requests
import time

@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Fetches data from REST API with exponential backoff (Req 1.4).
    """
    url = kwargs.get('api_url', 'https://api.example.com/v1/data') # Placeholder
    headers = {
        'Authorization': f"Bearer {kwargs.get('api_token', 'your_token_here')}"
    }
    
    max_retries = 3
    retry_delay = 60 # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            # Wrap in list if it's a single object
            if isinstance(data, dict):
                data = [data]
            
            return pd.DataFrame(data)
            
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                sleep_time = retry_delay * (2 ** attempt)
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise Exception(f"Failed to fetch data after {max_retries} attempts (Req 1.5).")

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, pd.DataFrame), 'Output should be a pandas DataFrame'
