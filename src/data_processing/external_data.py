"""
Fetch and integrate external economic data.

This module handles:
- Exchange rate data from Frankfurter API
- Commodity prices from FRED API
- Merging external data with trade data
"""

import requests
import pandas as pd
from datetime import date
from typing import Optional, Dict
from fredapi import Fred
import logging

logger = logging.getLogger(__name__)


def _next_month_id(series: pd.Series) -> pd.Series:
    """
    Calculate YYYYMM of the following month for a series of month_id values.
    
    Parameters
    ----------
    series : pd.Series
        Series of month IDs in YYYYMM format (int or str)
        
    Returns
    -------
    pd.Series
        Next month IDs as integers
    """
    s = series.astype(str).str[:6]  # 'YYYYMM'
    dt = pd.to_datetime(s + "01", format="%Y%m%d")
    next_month = (dt.dt.to_period("M") + 1).dt.strftime("%Y%m")
    return next_month.astype(int)


def fetch_exchange_rates(
    start: str = "2022-12-31",
    end: str = "2024-11-30",
    base: str = "USD"
) -> pd.DataFrame:
    """
    Fetch monthly exchange rates from Frankfurter API.
    
    Parameters
    ----------
    start : str
        Start date (YYYY-MM-DD)
    end : str
        End date (YYYY-MM-DD)
    base : str
        Base currency code
        
    Returns
    -------
    pd.DataFrame
        Exchange rates with month_id_join column for merging
    """
    logger.info(f"Fetching exchange rates from {start} to {end}")
    
    period_range = pd.period_range(start=start, end=end, freq="M")
    all_data = {}
    
    for period in period_range:
        date_str = period.end_time.strftime("%Y-%m-%d")
        url = f"https://api.frankfurter.app/{date_str}?from={base}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            all_data[date_str] = data.get("rates", {})
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch rates for {date_str}: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame.from_dict(all_data, orient="index").sort_index()
    df.index = pd.to_datetime(df.index)
    df["month_id"] = df.index.strftime("%Y%m")
    df["month_id_join"] = _next_month_id(df["month_id"])
    df = df.drop(columns=["month_id"])
    
    logger.info(f"Fetched exchange rates for {len(df)} months")
    
    return df


def fetch_commodity_prices(
    api_key: str,
    start: str = "2022-12-31",
    end: str = "2024-11-30"
) -> pd.DataFrame:
    """
    Fetch commodity prices from FRED API.
    
    Parameters
    ----------
    api_key : str
        FRED API key
    start : str
        Start date (YYYY-MM-DD)
    end : str
        End date (YYYY-MM-DD)
        
    Returns
    -------
    pd.DataFrame
        Commodity prices with month_id_join column for merging
    """
    logger.info(f"Fetching commodity prices from FRED")
    
    fred = Fred(api_key=api_key)
    
    # Commodity series codes
    series_dict = {
        # Energy
        "Crude Oil (WTI)": "DCOILWTICO",
        "Brent Oil": "DCOILBRENTEU",
        "Natural Gas (Henry Hub)": "DHHNGSP",
        # Metals
        "Copper": "PCOPPUSDM",
        "Aluminum": "PALUMUSDM",
        "Nickel": "PNICKUSDM",
        "Zinc": "PZINCUSDM",
        "Tin": "PTINUSDM",
        "Lead": "PLEADUSDM",
        "Iron Ore": "PIORECRUSDM",
        # Agriculture
        "Wheat": "PWHEAMTUSDM",
        "Corn": "PMAIZMTUSDM",
        "Soybeans": "PSOYBUSDM",
        "Rice (Thailand)": "PRICENPQUSDM",
        "Coffee (Arabica)": "PCOFFOTMUSDM",
        "Cocoa": "PCOCOUSDM",
        "Sugar No.11": "PSUGAISAUSDM",
        "Cotton": "PCOTTINDUSDM",
    }
    
    all_series = []
    for name, code in series_dict.items():
        try:
            series = fred.get_series(code, observation_start=start, observation_end=end)
            series = series.to_frame(name=name)
            series = series.resample("M").last()
            all_series.append(series)
            logger.info(f"  Fetched {name}")
        except Exception as e:
            logger.warning(f"  Failed to fetch {name} ({code}): {e}")
            continue
    
    # Concatenate all series
    df = pd.concat(all_series, axis=1)
    
    # Add month_id
    df["month_id"] = df.index.strftime("%Y%m")
    cols = ["month_id"] + [c for c in df.columns if c != "month_id"]
    df = df[cols].reset_index(drop=True)
    df["month_id_join"] = _next_month_id(df["month_id"])
    df = df.drop(columns=["month_id"])
    
    logger.info(f"Fetched {len(all_series)} commodity price series")
    
    return df


def merge_external_data(
    trade_data: Dict[str, pd.DataFrame],
    exchange_rates: pd.DataFrame,
    commodity_prices: pd.DataFrame,
    output_dir: Optional[pd.DataFrame] = None
) -> Dict[str, pd.DataFrame]:
    """
    Merge external data (exchange rates, commodities) with trade data.
    
    Parameters
    ----------
    trade_data : Dict[str, pd.DataFrame]
        Dictionary of trade dataframes
    exchange_rates : pd.DataFrame
        Exchange rate data with month_id_join column
    commodity_prices : pd.DataFrame
        Commodity price data with month_id_join column
    output_dir : Path, optional
        Directory to save merged files
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of merged dataframes
    """
    logger.info("Merging external data with trade data")
    
    merged_tables = {}
    
    for name, df in trade_data.items():
        logger.info(f"  Processing {name}")
        
        # Merge exchange rates
        df_merged = df.merge(
            exchange_rates,
            left_on="month_id",
            right_on="month_id_join",
            how="left"
        ).drop(columns="month_id_join")
        
        # Merge commodity prices
        df_merged = df_merged.merge(
            commodity_prices,
            left_on="month_id",
            right_on="month_id_join",
            how="left"
        ).drop(columns="month_id_join")
        
        merged_tables[f"{name}_vf"] = df_merged
        
        # Save if output directory provided
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{name}_vf.csv"
            df_merged.to_csv(output_file, index=False, encoding="utf-8")
            logger.info(f"  Saved {output_file}")
    
    return merged_tables


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    exchange_rates = fetch_exchange_rates()
    exchange_rates.to_csv("outputs/interim/exchange_rates.csv", index=False)
    
    # Note: Requires FRED API key
    # commodity_prices = fetch_commodity_prices(api_key="YOUR_API_KEY")
    # commodity_prices.to_csv("outputs/interim/commodity_prices.csv", index=False)

