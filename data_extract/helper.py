from datetime import datetime
import pandas as pd
from typing import List

class Helper:
    def __init__(self):
        pass

    def date_from_epoch(self, epoch_date: float) -> str:
        if epoch_date > 1e10:  # This means the epoch is in milliseconds
            epoch_date /= 1000 # Convert date to seconds

        date_str = datetime.fromtimestamp(epoch_date).strftime('%Y-%m-%d %H:%M:%S')
        return date_str
    
    def merge_and_sum(self, existing_df: pd.DataFrame, new_df: pd.DataFrame, key_columns: List[str], sum_columns: List[str]) -> pd.DataFrame:
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, new_df])
            combined_df = combined_df.groupby(key_columns, as_index=False)[sum_columns].sum()
            return combined_df
        else:
            return new_df