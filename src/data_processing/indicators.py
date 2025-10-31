"""
Add economic indicators (GDP, REER) to trade data.

This module handles integration of:
- GDP and other economic indicators from World Bank
- REER (Real Effective Exchange Rate) from IMF
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def read_csv_with_encoding(file_path: Path) -> pd.DataFrame:
    """Try different encodings to read CSV."""
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except:
            continue
    raise Exception(f"Could not read file: {file_path}")


def prepare_indicators_data(
    indicators_file: Path,
    price_type: str = 'Constant prices',
    adjustment: str = 'Seasonally adjusted (SA)'
) -> pd.DataFrame:
    """
    Load and prepare economic indicators data.
    
    Parameters
    ----------
    indicators_file : Path
        Path to indicators CSV file (df_long.csv format)
    price_type : str
        Price type to filter (e.g., 'Constant prices')
    adjustment : str
        Seasonal adjustment to filter
        
    Returns
    -------
    pd.DataFrame
        Wide-format indicators with country_id and month_id columns
    """
    logger.info(f"Loading indicators from {indicators_file}")
    
    df = read_csv_with_encoding(indicators_file)
    
    # Filter for relevant indicators
    indicator_keywords = ['GDP', 'consumption expenditure', 'capital formation', 'inventories']
    
    df_filtered = df[
        (df['PRICE_TYPE'] == price_type) &
        (df['S_ADJUSTMENT'] == adjustment) &
        (df['INDICATOR'].apply(
            lambda x: any(keyword.lower() in x.lower() for keyword in indicator_keywords)
        ))
    ].copy()
    
    logger.info(f"Filtered to {len(df_filtered):,} indicator observations")
    
    # Pivot to wide format
    df_wide = df_filtered.pivot_table(
        index=['ISO3', 'PERIOD'],
        columns='INDICATOR',
        values='VALUE',
        aggfunc='first'
    ).reset_index()
    
    # Rename columns
    column_rename = {
        'ISO3': 'country_id',
        'PERIOD': 'month_id'
    }
    
    # Create standardized column names for indicators
    for col in df_wide.columns:
        if 'GDP' in col or 'Gross domestic product' in col:
            column_rename[col] = 'gdp_constant_sa'
        elif 'Final consumption expenditure' in col:
            column_rename[col] = 'final_consumption_constant_sa'
        elif 'Gross capital formation' in col:
            column_rename[col] = 'gross_capital_formation_constant_sa'
        elif 'Changes in inventories' in col:
            column_rename[col] = 'changes_inventories_constant_sa'
    
    df_wide = df_wide.rename(columns=column_rename)
    
    logger.info(f"Prepared indicators: {df_wide.shape}")
    
    return df_wide


def prepare_reer_data(reer_file: Path) -> pd.DataFrame:
    """
    Load and prepare REER (Real Effective Exchange Rate) data.
    
    Parameters
    ----------
    reer_file : Path
        Path to REER CSV file (EER_COUNTRIES.csv format)
        
    Returns
    -------
    pd.DataFrame
        Long-format REER data with country_id, month_id, REER columns
    """
    logger.info(f"Loading REER from {reer_file}")
    
    df = read_csv_with_encoding(reer_file)
    
    # Filter for REER indicator
    df_filtered = df[df['INDICATOR'].str.contains('REER', case=False, na=False)].copy()
    
    # Get date columns (format: 2021-M01, 2021-M02, etc.)
    date_columns = [col for col in df_filtered.columns if '-M' in col]
    logger.info(f"Found {len(date_columns)} date columns")
    
    # Melt to long format
    df_long = df_filtered.melt(
        id_vars=['COUNTRY.ID'],
        value_vars=date_columns,
        var_name='period_str',
        value_name='REER'
    )
    
    # Convert period format from "2021-M01" to "202101"
    df_long['month_id'] = df_long['period_str'].str.replace('-M', '').astype(int)
    df_long = df_long.rename(columns={'COUNTRY.ID': 'country_id'})
    
    # Keep only relevant columns and remove NaNs
    df_final = df_long[['country_id', 'month_id', 'REER']].dropna(subset=['REER'])
    
    logger.info(f"Prepared REER data: {len(df_final):,} observations")
    
    return df_final


def add_economic_indicators(
    trade_data: pd.DataFrame,
    indicators_data: pd.DataFrame,
    reer_data: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Add economic indicators and REER to trade data.
    
    Parameters
    ----------
    trade_data : pd.DataFrame
        Trade data with country_id and month_id columns
    indicators_data : pd.DataFrame
        Indicators data (from prepare_indicators_data)
    reer_data : pd.DataFrame, optional
        REER data (from prepare_reer_data)
        
    Returns
    -------
    pd.DataFrame
        Trade data with added indicator columns
    """
    logger.info("Adding economic indicators to trade data")
    
    # Ensure country_id is uppercase
    if 'country_id' in trade_data.columns:
        trade_data = trade_data.copy()
        trade_data['country_id'] = trade_data['country_id'].str.upper()
    
    # Merge indicators
    df_merged = trade_data.merge(
        indicators_data,
        on=['country_id', 'month_id'],
        how='left'
    )
    
    indicator_cols = [col for col in df_merged.columns if '_constant_sa' in col]
    rows_with_indicators = df_merged[indicator_cols].notna().any(axis=1).sum()
    logger.info(f"  Added {len(indicator_cols)} indicator columns")
    logger.info(f"  Rows with at least one indicator: {rows_with_indicators:,}")
    
    # Merge REER if provided
    if reer_data is not None:
        df_merged = df_merged.merge(
            reer_data,
            on=['country_id', 'month_id'],
            how='left'
        )
        rows_with_reer = df_merged['REER'].notna().sum()
        logger.info(f"  Added REER column")
        logger.info(f"  Rows with REER data: {rows_with_reer:,}")
    
    return df_merged


def add_indicators_to_files(
    input_dir: Path,
    output_dir: Path,
    indicators_file: Path,
    reer_file: Path,
    file_pattern: str = "*_final.csv"
) -> Dict[str, pd.DataFrame]:
    """
    Add indicators to multiple trade data files.
    
    Parameters
    ----------
    input_dir : Path
        Directory containing trade data files
    output_dir : Path
        Directory to save files with indicators
    indicators_file : Path
        Path to indicators CSV
    reer_file : Path
        Path to REER CSV
    file_pattern : str
        Glob pattern for files to process
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of processed dataframes
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare reference data
    indicators_data = prepare_indicators_data(indicators_file)
    reer_data = prepare_reer_data(reer_file)
    
    processed_files = {}
    
    # Process each file
    for file_path in input_dir.glob(file_pattern):
        logger.info(f"\nProcessing {file_path.name}")
        
        try:
            # Load trade data
            df = read_csv_with_encoding(file_path)
            logger.info(f"  Original rows: {len(df):,}")
            
            # Add indicators
            df_merged = add_economic_indicators(df, indicators_data, reer_data)
            
            # Save
            output_filename = file_path.name.replace('_final.csv', '_Additional.csv')
            output_path = output_dir / output_filename
            df_merged.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"  Saved: {output_filename}")
            logger.info(f"  Total columns: {len(df_merged.columns)}")
            
            processed_files[output_filename] = df_merged
            
        except Exception as e:
            logger.error(f"  Error processing {file_path.name}: {e}")
            continue
    
    return processed_files


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    input_dir = Path("outputs/processed")
    output_dir = Path("outputs/processed_with_indicators")
    indicators_file = Path("inputs/reference/df_long.csv")
    reer_file = Path("inputs/reference/EER_COUNTRIES.csv")
    
    add_indicators_to_files(input_dir, output_dir, indicators_file, reer_file)

