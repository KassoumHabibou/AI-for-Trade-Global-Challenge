"""
Data processing module for AI4Trade Challenge.

This module handles:
- Raw trade data processing (2023-2024 datasets)
- External data integration (exchange rates, commodity prices)
- Comtrade data processing (2021, 2022, 2025 datasets)
- Economic indicators integration (GDP, REER from World Bank/IMF)
"""

from .process_trade_data import process_trade_files, prepare_table
from .external_data import fetch_exchange_rates, fetch_commodity_prices, merge_external_data
from .comtrade_processor import process_comtrade_files, normalize_comtrade_data
from .indicators import add_economic_indicators, add_reer_data

__all__ = [
    'process_trade_files',
    'prepare_table',
    'fetch_exchange_rates',
    'fetch_commodity_prices',
    'merge_external_data',
    'process_comtrade_files',
    'normalize_comtrade_data',
    'add_economic_indicators',
    'add_reer_data',
]

