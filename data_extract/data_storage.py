import pandas as pd
import os
import logging
from typing import Optional, Dict

# Import the logging configuration
from logging_config import setup_logging

# Set up logging
logger = setup_logging()

class DataStorage:
    def __init__(self):
        pass

    def read_excel(self, path: str, schema: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        logger.info(f'Reading Excel from: {path}')
        df = pd.read_excel(path)
        if schema:
            # Convert DataFrame columns to the specified data types
            for column, dtype in schema.items():
                logger.info(f'Column : {column}, dtype : {dtype}')
                df[column] = df[column].astype(dtype)
        
        return df

    def output_excel(self, path: str, df: pd.DataFrame, schema: Optional[Dict[str, str]] = None, append: bool = False) -> None:
        logger.info(f'Outputting Excel to: {path}')
        if schema:
            # Convert DataFrame columns to the specified data types
            for column, dtype in schema.items():
                logger.info(f'Column :{column}, dtype :{dtype}')
                df[column] = df[column].astype(dtype)
        
        if os.path.exists(path) and append:
            existing_df = self.read_excel(path=path, schema=schema)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_excel(path, index=False)