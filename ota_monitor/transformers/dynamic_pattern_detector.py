from mage_ai.data_preparation.decorators import transformer, test
from pandas import DataFrame
import json
import os
import importlib.util
import sys

@transformer
def dynamic_pattern_detector(df: DataFrame, *args, **kwargs) -> DataFrame:
    """
    Dynamically loads and executes pattern detection plugins from the plugins/ directory.
    """
    if df.empty:
        return DataFrame(columns=['pattern_type', 'occurrence_count'])

    # 1. Standardize/Parse Data for Plugins
    records = []
    for _, row in df.iterrows():
        try:
            payload = json.loads(row['raw_payload'])
            body = payload.get('contentJson', {}).get('requestBody', {})
            records.append({
                'vin': body.get('vin'),
                'updateTime': body.get('updateTime'),
                'usageModeName': body.get('usageModeName'),
                'raw_id': payload.get('id')
            })
        except Exception as e:
            print(f"Error parsing record: {e}")
            continue

    standard_df = DataFrame(records)
    if standard_df.empty:
        return DataFrame(columns=['pattern_type', 'occurrence_count', 'id'])

    # ... Discover and Run Plugins ...
    all_stats = []
    # (rest of discovery logic)
    plugins_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')
    
    # Add plugins dir to path for imports
    if plugins_dir not in sys.path:
        sys.path.append(plugins_dir)

    for filename in os.listdir(plugins_dir):
        if filename.startswith('rule_') and filename.endswith('.py'):
            module_name = filename[:-3]
            try:
                # Dynamic import
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(plugins_dir, filename))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'evaluate_rule'):
                    print(f"Executing plugin: {module_name}")
                    plugin_results = module.evaluate_rule(standard_df)
                    all_stats.extend(plugin_results)
                else:
                    print(f"Plugin {filename} missing evaluate_rule function.")
            except Exception as e:
                print(f"Failed to execute plugin {filename}: {e}")

    if not all_stats:
        return DataFrame(columns=['pattern_type', 'occurrence_count'])

    # 3. Aggregate Results
    results_df = DataFrame(all_stats)
    aggregated = results_df.groupby('pattern_type')['occurrence_count'].sum().reset_index()
    
    return aggregated

@test
def test_output(output, *args) -> None:
    assert output is not None
    assert 'pattern_type' in output.columns
    assert 'occurrence_count' in output.columns
