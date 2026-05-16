import sys
from unittest.mock import MagicMock

def identity(func):
    return func

# Identity decorators
mock_decorators = MagicMock()
mock_decorators.transformer = identity
mock_decorators.test = identity
mock_decorators.data_loader = identity
mock_decorators.data_exporter = identity

# Create mocks for the sub-packages
mock_mage = MagicMock()
mock_io = MagicMock()
mock_settings = MagicMock()

# Structure the modules correctly
sys.modules['mage_ai'] = mock_mage
sys.modules['mage_ai.data_preparation'] = mock_mage
sys.modules['mage_ai.data_preparation.decorators'] = mock_decorators
sys.modules['mage_ai.io'] = mock_io
sys.modules['mage_ai.io.config'] = MagicMock()
sys.modules['mage_ai.io.http'] = MagicMock()
sys.modules['mage_ai.io.postgres'] = MagicMock()
sys.modules['mage_ai.settings'] = mock_settings
sys.modules['mage_ai.settings.repo'] = MagicMock()
