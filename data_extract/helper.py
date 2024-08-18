from datetime import datetime
import pandas as pd

class Helper:
    def __init__():
        pass

    def date_from_epoch(self, epoch_date):
        if epoch_date > 1e10:  # This means the epoch is in milliseconds
            epoch_date /= 1000 # Convert date to seconds

        date_str = datetime.fromtimestamp(epoch_date).strftime('%Y-%m-%d %H:%M:%S')
        return date_str
    
    def merge_and_sum(self, existing_df, new_df, key_columns, sum_columns):
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, new_df])
            combined_df = combined_df.groupby(key_columns, as_index=False)[sum_columns].sum()
            return combined_df
        else:
            return new_df