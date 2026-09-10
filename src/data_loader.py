"""
data_loader.py
==============
Module for loading raw and processed healthcare benefits datasets,
verifying structural integrity, and logging file metadata.
"""

import os
from typing import Optional, Tuple
import pandas as pd

def load_raw_data(filepath: str = 'data/raw/employee_health_benefits_raw.csv') -> pd.DataFrame:
    """
    Loads the raw employee health benefits CSV file.
    Performs initial file existence check and basic structural assertions.

    Parameters:
        filepath (str): Relative or absolute path to the raw CSV file.

    Returns:
        pd.DataFrame: Loaded raw DataFrame.

    Raises:
        FileNotFoundError: If the specified data file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'. Please run 'src/data_generator.py' first."
        )

    df = pd.read_csv(filepath)
    return df

def inspect_dataset_schema(df: pd.DataFrame) -> dict:
    """
    Analyzes the schema of the provided DataFrame, returning summary statistics
    including row counts, columns, memory footprint, and data types.

    Parameters:
        df (pd.DataFrame): Target dataframe.

    Returns:
        dict: Diagnostic metadata dictionary.
    """
    info = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'memory_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'null_counts': {col: int(cnt) for col, cnt in df.isna().sum().items() if cnt > 0},
        'duplicate_rows': int(df.duplicated().sum())
    }
    return info

if __name__ == '__main__':
    raw_df = load_raw_data()
    summary = inspect_dataset_schema(raw_df)
    print("Schema Inspection for Raw Dataset:")
    print(f"Total Rows: {summary['row_count']:,}")
    print(f"Total Columns: {summary['column_count']}")
    print(f"Memory Usage: {summary['memory_mb']} MB")
    print(f"Columns with Missing Values: {summary['null_counts']}")
    print(f"Duplicate Rows Detected: {summary['duplicate_rows']}")
