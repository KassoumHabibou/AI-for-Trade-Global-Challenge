"""
Process Comtrade monthly HS4 data.

This module handles processing of additional Comtrade datasets (2021, 2022, 2025)
for USA and China, including data normalization and filtering.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from glob import glob
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def read_csv_with_encoding(file_path: Path) -> pd.DataFrame:
    """
    Read CSV with correct encoding, handling missing column names.
    
    Parameters
    ----------
    file_path : Path
        Path to CSV file
        
    Returns
    -------
    pd.DataFrame
        Loaded dataframe
    """
    encodings = ['latin-1', 'iso-8859-1', 'windows-1252', 'utf-8']
    
    for encoding in encodings:
        try:
            # First read to get header and data line
            with open(file_path, 'r', encoding=encoding) as f:
                header_line = f.readline().strip()
                data_line = f.readline().strip()
            
            # Count columns
            header_cols = header_line.count(',') + 1
            data_cols = data_line.count(',') + 1
            
            if data_cols > header_cols:
                # Add placeholder names for missing columns
                missing_cols = data_cols - header_cols
                logger.debug(f"Adding {missing_cols} placeholder columns for {file_path.name}")
                
                df_temp = pd.read_csv(file_path, encoding=encoding, nrows=0)
                original_columns = df_temp.columns.tolist()
                new_columns = original_columns + [f'unnamed_col_{i}' for i in range(missing_cols)]
                
                df = pd.read_csv(file_path, encoding=encoding, names=new_columns, skiprows=1)
            else:
                df = pd.read_csv(file_path, encoding=encoding)
            
            return df
            
        except (UnicodeDecodeError, Exception):
            continue
    
    raise Exception(f"Could not read file with any encoding: {file_path}")


def process_comtrade_files(
    input_dir: Path,
    output_dir: Path,
    years: List[int],
    country: str = "USA"
) -> Dict[str, pd.DataFrame]:
    """
    Process Comtrade monthly HS4 files for specified years.
    
    Parameters
    ----------
    input_dir : Path
        Directory containing raw Comtrade CSV files
    output_dir : Path
        Directory to save merged files
    years : List[int]
        Years to process
    country : str
        Country code (USA or CHN)
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of merged dataframes by year and trade type
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    trade_types = {'M': 'import', 'X': 'export'}
    processed_files = {}
    
    for year in years:
        for trade_code, trade_name in trade_types.items():
            logger.info(f"Processing {country} {year} {trade_name}...")
            
            # Find matching files
            pattern = str(input_dir / f"{country}_{trade_code}_{year}*_HS4.csv")
            files = sorted(glob(pattern))
            
            if not files:
                logger.warning(f"No files found for {country} {year} {trade_name}")
                continue
            
            logger.info(f"  Found {len(files)} files")
            
            # Read and filter files
            dfs = []
            for file in files:
                try:
                    df = read_csv_with_encoding(Path(file))
                    
                    # Check for qty column and filter
                    if 'qty' not in df.columns:
                        logger.warning(f"'qty' column not found in {Path(file).name}")
                        continue
                    
                    df_filtered = df[df['qty'] >= 0]
                    dfs.append(df_filtered)
                    logger.debug(f"  {Path(file).name}: {len(df)} -> {len(df_filtered)} rows")
                    
                except Exception as e:
                    logger.error(f"Error reading {Path(file).name}: {e}")
            
            # Concatenate and save
            if dfs:
                merged_df = pd.concat(dfs, ignore_index=True)
                
                output_file = output_dir / f"{country}_{year}_{trade_name}.csv"
                merged_df.to_csv(output_file, index=False, encoding='utf-8')
                
                logger.info(f"  Saved {output_file.name}: {len(merged_df):,} rows")
                processed_files[f"{country}_{year}_{trade_name}"] = merged_df
            else:
                logger.warning(f"No data to merge for {country} {year} {trade_name}")
    
    return processed_files


def normalize_comtrade_data(
    input_file: Path,
    output_file: Path,
    min_products: int = 200
) -> pd.DataFrame:
    """
    Normalize Comtrade data to standard format.
    
    This function:
    1. Renames columns to standard names
    2. Converts product_id to HS4 level
    3. Calculates nb_product per country-month
    4. Filters by minimum product count
    
    Parameters
    ----------
    input_file : Path
        Path to raw Comtrade CSV file
    output_file : Path
        Path to save normalized file
    min_products : int
        Minimum number of products per country-month
        
    Returns
    -------
    pd.DataFrame
        Normalized dataframe
    """
    # Column mapping from Comtrade to standard format
    column_mapping = {
        'period': 'month_id',
        'flowDesc': 'trade_flow_name',
        'partnerISO': 'country_id',
        'partnerDesc': 'country_name',
        'cmdCode': 'product_id_hs4',
        'primaryValue': 'trade_value',
        'qty': 'quantity',
        'cmdDesc': 'product_name_hs4'
    }
    
    # Final column order
    final_columns = [
        'month_id', 'trade_flow_name', 'country_id', 'country_name',
        'product_id_hs4', 'trade_value', 'quantity', 'nb_product', 'product_name_hs4'
    ]
    
    logger.info(f"Normalizing {input_file.name}...")
    
    # Read file
    df = read_csv_with_encoding(input_file)
    
    # Check for required columns
    missing_cols = [col for col in column_mapping.keys() if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Select and rename columns
    df_selected = df[list(column_mapping.keys())].copy()
    df_renamed = df_selected.rename(columns=column_mapping)
    
    # Convert product_id to string
    df_renamed['product_id_hs4'] = df_renamed['product_id_hs4'].astype(str)
    
    # Calculate nb_product per month-country
    df_renamed['nb_product'] = df_renamed.groupby(
        ['month_id', 'country_id']
    )['product_id_hs4'].transform('nunique')
    
    # Filter by minimum products
    df_filtered = df_renamed[df_renamed['nb_product'] > min_products].copy()
    
    # Reorder columns
    df_final = df_filtered[final_columns]
    
    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_file, index=False, encoding='utf-8')
    
    logger.info(f"  Normalized: {len(df):,} -> {len(df_final):,} rows")
    logger.info(f"  Saved: {output_file}")
    
    return df_final


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    input_dir = Path("inputs/raw/comtrade_monthly_hs4_outputs")
    output_dir = Path("outputs/interim/comtrade_merged")
    
    # Process USA files
    process_comtrade_files(input_dir, output_dir, years=[2021, 2022, 2025], country="USA")

