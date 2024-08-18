from datetime import datetime
import pandas as pd

class Helper():
    def __init__():
        pass

    def date_from_epoch(self, epoch_date):
        if epoch_date > 1e10:  # This means the epoch is in milliseconds
            epoch_date /= 1000 # Convert date to seconds

        date_str = datetime.fromtimestamp(epoch_date).strftime('%Y-%m-%d %H:%M:%S')
        return date_str