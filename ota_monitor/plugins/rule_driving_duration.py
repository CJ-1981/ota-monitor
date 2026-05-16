from pandas import DataFrame, to_datetime

def evaluate_rule(df: DataFrame) -> list:
    """
    Plugin logic for detecting DRIVING patterns lasting more than 3 or 10 minutes.
    """
    if df.empty:
        return []

    processed_df = df.copy()
    processed_df['updateTime'] = to_datetime(processed_df['updateTime'])
    
    # Sort by VIN and Time to calculate durations
    processed_df = processed_df.sort_values(['vin', 'updateTime'])
    
    # Calculate duration of contiguous states
    processed_df['state_changed'] = (processed_df['usageModeName'] != processed_df['usageModeName'].shift(1)) | \
                                   (processed_df['vin'] != processed_df['vin'].shift(1))
    processed_df['group_id'] = processed_df['state_changed'].cumsum()
    
    state_groups = processed_df.groupby(['group_id', 'vin', 'usageModeName']).agg(
        start_time=('updateTime', 'min'),
        end_time=('updateTime', 'max')
    ).reset_index()
    
    state_groups['duration_min'] = (state_groups['end_time'] - state_groups['start_time']).dt.total_seconds() / 60
    
    driving_stats = []
    
    # Critical: DRIVING > 10 min
    critical = state_groups[(state_groups['usageModeName'] == 'DRIVING') & (state_groups['duration_min'] > 10)]
    if not critical.empty:
        driving_stats.append({'pattern_type': 'DRIVING_CRITICAL_10MIN', 'occurrence_count': len(critical)})
        
    # Warning: DRIVING > 3 min
    warning = state_groups[(state_groups['usageModeName'] == 'DRIVING') & 
                          (state_groups['duration_min'] > 3) & 
                          (state_groups['duration_min'] <= 10)]
    if not warning.empty:
        driving_stats.append({'pattern_type': 'DRIVING_WARNING_3MIN', 'occurrence_count': len(warning)})

    return driving_stats
