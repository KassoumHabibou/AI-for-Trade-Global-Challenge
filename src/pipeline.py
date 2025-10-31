"""
Complete data processing pipeline for AI4Trade Challenge.

This script orchestrates the entire data processing workflow:
1. Process raw trade data (2023-2024)
2. Fetch and integrate external data (exchange rates, commodities)
3. Process Comtrade data (2021, 2022, 2025)
4. Add economic indicators (GDP, REER)
"""

import logging
import argparse
from pathlib import Path
import yaml
from typing import Optional

from data_processing.process_trade_data import process_trade_files
from data_processing.external_data import (
    fetch_exchange_rates,
    fetch_commodity_prices,
    merge_external_data
)
from data_processing.comtrade_processor import (
    process_comtrade_files,
    normalize_comtrade_data
)
from data_processing.indicators import add_indicators_to_files

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "configs/config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def run_pipeline(
    config_path: str = "configs/config.yaml",
    fred_api_key: Optional[str] = None,
    skip_external: bool = False,
    skip_comtrade: bool = False,
    skip_indicators: bool = False
):
    """
    Run the complete data processing pipeline.
    
    Parameters
    ----------
    config_path : str
        Path to configuration YAML file
    fred_api_key : str, optional
        FRED API key for commodity prices
    skip_external : bool
        Skip fetching external data (exchange rates, commodities)
    skip_comtrade : bool
        Skip processing Comtrade data
    skip_indicators : bool
        Skip adding economic indicators
    """
    logger.info("=" * 60)
    logger.info("AI4TRADE DATA PROCESSING PIPELINE")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_config(config_path)
    paths = config['paths']
    data_config = config.get('data_processing', {})
    
    # Define paths
    raw_dir = Path(paths['raw'])
    processed_dir = Path(paths['processed'])
    interim_dir = Path(paths['interim'])
    reference_dir = Path(paths['reference'])
    
    # Create directories
    for dir_path in [processed_dir, interim_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # ===================================================================
    # STEP 1: Process main trade data (2023-2024)
    # ===================================================================
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: Processing main trade data (2023-2024)")
    logger.info("=" * 60)
    
    hs4_codes_file = reference_dir / data_config.get('hs4_codes_file', 'code_hs4.xlsx')
    min_products = data_config.get('min_products', 200)
    
    try:
        trade_data = process_trade_files(
            input_dir=raw_dir / "ForParticipants",
            output_dir=processed_dir,
            hs4_codes_file=hs4_codes_file,
            min_products=min_products
        )
        logger.info(f"✓ Processed {len(trade_data)} trade datasets")
    except Exception as e:
        logger.error(f"✗ Failed to process trade data: {e}")
        raise
    
    # ===================================================================
    # STEP 2: Fetch and merge external data
    # ===================================================================
    if not skip_external:
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: Fetching external data")
        logger.info("=" * 60)
        
        try:
            # Exchange rates
            logger.info("Fetching exchange rates...")
            exchange_rates = fetch_exchange_rates(
                start=data_config.get('start_date', '2022-12-31'),
                end=data_config.get('end_date', '2024-11-30')
            )
            exchange_rates.to_csv(interim_dir / "exchange_rates.csv", index=False)
            logger.info("✓ Saved exchange rates")
            
            # Commodity prices (if API key provided)
            if fred_api_key:
                logger.info("Fetching commodity prices...")
                commodity_prices = fetch_commodity_prices(
                    api_key=fred_api_key,
                    start=data_config.get('start_date', '2022-12-31'),
                    end=data_config.get('end_date', '2024-11-30')
                )
                commodity_prices.to_csv(interim_dir / "commodity_prices.csv", index=False)
                logger.info("✓ Saved commodity prices")
                
                # Merge with trade data
                logger.info("Merging external data with trade data...")
                trade_data_with_external = merge_external_data(
                    trade_data=trade_data,
                    exchange_rates=exchange_rates,
                    commodity_prices=commodity_prices,
                    output_dir=processed_dir / "with_external"
                )
                logger.info(f"✓ Merged external data into {len(trade_data_with_external)} datasets")
            else:
                logger.warning("FRED API key not provided, skipping commodity prices")
                
        except Exception as e:
            logger.error(f"✗ Failed to fetch/merge external data: {e}")
            logger.warning("Continuing without external data...")
    
    # ===================================================================
    # STEP 3: Process Comtrade data (2021, 2022, 2025)
    # ===================================================================
    if not skip_comtrade:
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: Processing Comtrade data")
        logger.info("=" * 60)
        
        comtrade_raw_dir = raw_dir / "comtrade_monthly_hs4_outputs"
        comtrade_merged_dir = interim_dir / "comtrade_merged"
        comtrade_final_dir = processed_dir / "comtrade_final"
        
        if comtrade_raw_dir.exists():
            try:
                # Process USA files
                logger.info("Processing USA Comtrade files...")
                usa_files = process_comtrade_files(
                    input_dir=comtrade_raw_dir,
                    output_dir=comtrade_merged_dir,
                    years=data_config.get('comtrade_years', [2021, 2022, 2025]),
                    country="USA"
                )
                logger.info(f"✓ Processed {len(usa_files)} USA Comtrade files")
                
                # Process China files (if available)
                logger.info("Processing China Comtrade files...")
                china_files = process_comtrade_files(
                    input_dir=comtrade_raw_dir,
                    output_dir=comtrade_merged_dir,
                    years=data_config.get('comtrade_years', [2021, 2022]),
                    country="CHN"
                )
                logger.info(f"✓ Processed {len(china_files)} China Comtrade files")
                
                # Normalize files
                logger.info("Normalizing Comtrade data...")
                for file_path in comtrade_merged_dir.glob("*.csv"):
                    output_file = comtrade_final_dir / file_path.name.replace('.csv', '_final.csv')
                    normalize_comtrade_data(file_path, output_file, min_products=min_products)
                
                logger.info("✓ Normalized all Comtrade files")
                
            except Exception as e:
                logger.error(f"✗ Failed to process Comtrade data: {e}")
                logger.warning("Continuing without Comtrade data...")
        else:
            logger.warning(f"Comtrade directory not found: {comtrade_raw_dir}")
    
    # ===================================================================
    # STEP 4: Add economic indicators
    # ===================================================================
    if not skip_indicators:
        logger.info("\n" + "=" * 60)
        logger.info("STEP 4: Adding economic indicators")
        logger.info("=" * 60)
        
        indicators_file = reference_dir / data_config.get('indicators_file', 'df_long.csv')
        reer_file = reference_dir / data_config.get('reer_file', 'EER_COUNTRIES.csv')
        
        if indicators_file.exists() and reer_file.exists():
            try:
                # Add to main processed files
                logger.info("Adding indicators to main trade data...")
                add_indicators_to_files(
                    input_dir=processed_dir,
                    output_dir=processed_dir / "with_indicators",
                    indicators_file=indicators_file,
                    reer_file=reer_file,
                    file_pattern="*_finale.csv"
                )
                
                # Add to Comtrade files
                comtrade_final_dir = processed_dir / "comtrade_final"
                if comtrade_final_dir.exists():
                    logger.info("Adding indicators to Comtrade data...")
                    add_indicators_to_files(
                        input_dir=comtrade_final_dir,
                        output_dir=comtrade_final_dir / "with_indicators",
                        indicators_file=indicators_file,
                        reer_file=reer_file
                    )
                
                logger.info("✓ Added indicators to all files")
                
            except Exception as e:
                logger.error(f"✗ Failed to add indicators: {e}")
                logger.warning("Continuing without indicators...")
        else:
            logger.warning("Indicators or REER file not found, skipping...")
    
    # ===================================================================
    # PIPELINE COMPLETE
    # ===================================================================
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Processed data saved in: {processed_dir}")
    logger.info(f"Interim data saved in: {interim_dir}")


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description="Run AI4Trade data processing pipeline"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='configs/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--fred-api-key',
        type=str,
        help='FRED API key for commodity prices'
    )
    parser.add_argument(
        '--skip-external',
        action='store_true',
        help='Skip fetching external data'
    )
    parser.add_argument(
        '--skip-comtrade',
        action='store_true',
        help='Skip processing Comtrade data'
    )
    parser.add_argument(
        '--skip-indicators',
        action='store_true',
        help='Skip adding economic indicators'
    )
    
    args = parser.parse_args()
    
    run_pipeline(
        config_path=args.config,
        fred_api_key=args.fred_api_key,
        skip_external=args.skip_external,
        skip_comtrade=args.skip_comtrade,
        skip_indicators=args.skip_indicators
    )


if __name__ == "__main__":
    main()

