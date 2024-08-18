import pandas as pd
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_storage.log"),
        logging.StreamHandler()
    ]
)

class DataStorage:
    def __init__():
        pass

    def read_excel(self, path, schema=None):
        logging.info('Reading Excel from: ', path)
        df = pd.read_excel(path)
        if schema:
            # Convert DataFrame columns to the specified data types
            for column, dtype in schema.items():
                logging.info('Column :', column, 'dtype :', dtype)
                df[column] = df[column].astype(dtype)
        
        return df

    def output_excel(self, path, df, schema=None, append=False):
        logging.info('Outputting Excel to: ', path)
        if schema:
            # Convert DataFrame columns to the specified data types
            for column, dtype in schema.items():
                logging.info('Column :', column, 'dtype :', dtype)
                df[column] = df[column].astype(dtype)
        
        if os.path.exists(path) and append:
            existing_df = self.read_excel(path=path, schema=schema)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_excel(path, index=False)