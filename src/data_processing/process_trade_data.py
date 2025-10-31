"""
Process raw trade data (2023-2024 datasets).

This module processes the main trade datasets for USA and China,
aggregating to HS4 level and filtering countries with sufficient product diversity.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def load_hs4_codes(filepath: str) -> pd.DataFrame:
    """Load HS4 product code mappings."""
    return pd.read_excel(filepath, dtype={"product_id_hs4": str})


def prepare_table(
    df: pd.DataFrame,
    hs4_mapping: Dict[str, str],
    min_products: int = 200
) -> pd.DataFrame:
    """
    Prepare trade data table by:
    1. Selecting relevant columns
    2. Aggregating to HS4 level
    3. Filtering countries with sufficient product diversity
    4. Adding product names
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw trade data with columns: month_id, trade_flow_name, country_id,
        country_name, product_id, trade_value
    hs4_mapping : Dict[str, str]
        Mapping from HS4 codes to product names
    min_products : int, optional
        Minimum number of unique products required per country-month
        
    Returns
    -------
    pd.DataFrame
        Processed trade data at HS4 level
    """
    # Select base columns
    base_cols = [
        "month_id", "trade_flow_name", "country_id", 
        "country_name", "product_id", "trade_value"
    ]
    df = df[base_cols].copy()
    
    # Extract HS4 code (first 4 digits)
    df["product_id_hs4"] = df["product_id"].astype(str).str[:4]
    
    # Aggregate to HS4 level
    grp_cols = ["month_id", "trade_flow_name", "country_id", "country_name", "product_id_hs4"]
    aggregated = (
        df.groupby(grp_cols, as_index=False, sort=False)["trade_value"]
        .sum()
    )
    
    # Calculate product diversity per country-month
    nb_products = (
        aggregated.groupby(["month_id", "country_name", "country_id"])["product_id_hs4"]
        .nunique()
        .rename("nb_product")
        .reset_index()
    )
    
    # Merge back and filter
    result = aggregated.merge(nb_products, on=["month_id", "country_name", "country_id"], how="left")
    result = result[result["nb_product"] > min_products]
    
    # Add product names
    result["product_name_hs4"] = result["product_id_hs4"].map(hs4_mapping)
    
    logger.info(f"Processed {len(result):,} rows with {result['country_id'].nunique()} countries")
    
    return result


def process_trade_files(
    input_dir: Path,
    output_dir: Path,
    hs4_codes_file: Path,
    min_products: int = 200
) -> Dict[str, pd.DataFrame]:
    """
    Process all trade data files (USA and China, 2023-2024).
    
    Parameters
    ----------
    input_dir : Path
        Directory containing raw trade CSV files
    output_dir : Path
        Directory to save processed files
    hs4_codes_file : Path
        Path to HS4 code mapping Excel file
    min_products : int, optional
        Minimum number of products per country-month
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of processed dataframes by name
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load HS4 code mappings
    code_hs4 = load_hs4_codes(hs4_codes_file)
    hs4_name = dict(zip(code_hs4["product_id_hs4"], code_hs4["product_name_hs4"]))
    
    # Define input files
    files = {
        "USA_2023": input_dir / "trade_s_usa_state_m_hs_2023.csv",
        "USA_2024": input_dir / "trade_s_usa_state_m_hs_2024.csv",
        "china_2023": input_dir / "trade_s_chn_m_hs_2023.csv",
        "china_2024": input_dir / "trade_s_chn_m_hs_2024.csv",
    }
    
    processed_tables = {}
    
    for name, filepath in files.items():
        logger.info(f"Processing {name}...")
        
        # Read data
        df = pd.read_csv(filepath, dtype={"product_id": str})
        
        # Process table
        processed = prepare_table(df, hs4_name, min_products)
        
        # Save
        output_file = output_dir / f"{name}_finale.csv"
        processed.to_csv(output_file, index=False, encoding="utf-8")
        logger.info(f"Saved {output_file}")
        
        processed_tables[f"{name}_finale"] = processed
    
    return processed_tables


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    input_dir = Path("inputs/raw/ForParticipants")
    output_dir = Path("outputs/processed")
    hs4_codes_file = Path("inputs/reference/code_hs4.xlsx")
    
    process_trade_files(input_dir, output_dir, hs4_codes_file)

