# AI for Trade Global Challenge — Team SABLE Repository

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository contains our solution for the **AI for Trade Global Challenge** organized by the Center for Collective Learning (CCL) with the Observatory of Economic Complexity (OEC). The goal is to forecast international trade flows for the United States and China for October 2025.

## 🎯 Challenge Overview

- **Objective**: Forecast trade flows (imports & exports) for USA and China in October 2025
- **Scope**: Top 20 trading partners trading ≥200 HS4 products
- **Evaluation**: sMAPE (symmetric Mean Absolute Percentage Error)
- **Submission Deadline**: October 31, 2025 (CET, midnight)

Full challenge details available in [`docs/challenge_details.md`](docs/challenge_details.md)

---

## 📊 Our Approach

### Data Sources

Our solution integrates multiple data sources:

1. **Trade Data**
   - OEC trade data for USA & China (2023-2024) — main training data
   - UN Comtrade monthly HS4 data (2021, 2022, 2025) — additional historical context
   
2. **External Economic Data**
   - **Exchange Rates**: Monthly USD rates from [Frankfurter API](https://www.frankfurter.app/)
   - **Commodity Prices**: Energy, metals, and agricultural commodities from [FRED API](https://fred.stlouisfed.org/)
   
3. **Economic Indicators**
   - **GDP & Macroeconomic Indicators**: World Bank data (constant prices, seasonally adjusted)
   - **REER**: Real Effective Exchange Rate from IMF
   
### Methodology

Our forecasting pipeline consists of:

1. **Data Processing**: Aggregate trade data to HS4 level, filter countries with sufficient product diversity
2. **Feature Engineering**: Integrate economic indicators, exchange rates, and commodity prices
3. **Model Training**: Ensemble of gradient boosting models (CatBoost, XGBoost, LightGBM)
4. **Forecast Generation**: Predict October 2025 trade values for submission

---

## 🗂️ Repository Structure

```
AI-for-Trade-Global-Challenge/
│
├── README.md                          # This file - project overview
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
├── Makefile                          # Common commands
│
├── configs/
│   └── config.yaml                   # Centralized configuration
│
├── docs/
│   ├── challenge_details.md          # Full challenge description
│   └── data_pipeline.md              # Data processing documentation
│
├── inputs/                           # Input data (not versioned)
│   ├── raw/                          # Raw provided data
│   │   ├── ForParticipants/          # OEC training data (2023-2024)
│   │   └── comtrade_monthly_hs4_outputs/  # Comtrade data (2021,2022,2025)
│   ├── external/                     # External data sources
│   └── reference/                    # Lookups, code lists
│       ├── code_hs4.xlsx             # HS4 product code mappings
│       ├── df_long.csv               # Economic indicators (World Bank)
│       └── EER_COUNTRIES.csv         # REER data (IMF)
│
├── outputs/                          # Generated artifacts (not versioned)
│   ├── interim/                      # Intermediate processing results
│   │   ├── exchange_rates.csv        # Fetched exchange rates
│   │   ├── commodity_prices.csv      # Fetched commodity prices
│   │   └── comtrade_merged/          # Merged Comtrade files
│   ├── processed/                    # Final processed datasets
│   │   ├── USA_2023_finale.csv       # Processed USA 2023 data
│   │   ├── USA_2024_finale.csv       # Processed USA 2024 data
│   │   ├── china_2023_finale.csv     # Processed China 2023 data
│   │   ├── china_2024_finale.csv     # Processed China 2024 data
│   │   ├── with_external/            # Data with external variables
│   │   ├── with_indicators/          # Data with economic indicators
│   │   └── comtrade_final/           # Processed Comtrade data
│   ├── forecasts/                    # Final forecast CSVs
│   ├── evaluation/                   # Validation reports and scores
│   └── reports/                      # Figures, analysis, writeups
│
├── src/                              # Source code
│   ├── __init__.py
│   ├── pipeline.py                   # Main data processing pipeline
│   ├── data_processing/              # Data processing modules
│   │   ├── __init__.py
│   │   ├── process_trade_data.py     # Process 2023-2024 trade data
│   │   ├── external_data.py          # Fetch exchange rates & commodities
│   │   ├── comtrade_processor.py     # Process Comtrade data
│   │   └── indicators.py             # Add GDP, REER indicators
│   ├── metrics.py                    # sMAPE and evaluation metrics
│   ├── validate_submission.py        # Validate submission format
│   ├── evaluate.py                   # Compute sMAPE scores
│   └── forecast.py                   # Forecasting models
│
├── scripts/                          # Convenience scripts
│   ├── run_pipeline.sh               # Run complete data pipeline
│   ├── make_submission.sh            # Generate forecast submission
│   ├── validate_submission.sh        # Validate submission file
│   └── evaluate_submission.sh        # Evaluate against ground truth
│
├── notebooks/                        # Jupyter notebooks
│   ├── README.md                     # Notebook guidance
│   ├── SABLE_model_training.ipynb    # Main model training notebook
│   └── comtrade_data_processing.ipynb # Comtrade data processing
│
├── submissions/
│   ├── README.md                     # Submission guidelines
│   └── template_submission.csv       # Example submission format
│
├── tests/
│   └── test_metrics.py               # Unit tests
│
└── [Legacy files - to be deprecated]
    ├── 1_data_processing.py          # → moved to src/data_processing/
    └── 2_rajout_donnees_externes.py  # → moved to src/data_processing/
```

---

## 🚀 Quickstart

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/AI-for-Trade-Global-Challenge.git
cd AI-for-Trade-Global-Challenge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -U pip
pip install -r requirements.txt
```

### 2. Prepare Data

Download the required datasets and organize them:

```
inputs/
  raw/
    ForParticipants/
      trade_s_usa_state_m_hs_2023.csv
      trade_s_usa_state_m_hs_2024.csv
      trade_s_chn_m_hs_2023.csv
      trade_s_chn_m_hs_2024.csv
    comtrade_monthly_hs4_outputs/
      [Comtrade monthly files]
  reference/
    code_hs4.xlsx
    df_long.csv
    EER_COUNTRIES.csv
```

### 3. Run Data Processing Pipeline

Set your FRED API key (optional, for commodity prices):
```bash
export FRED_API_KEY="your_api_key_here"
```

Run the complete pipeline:
```bash
python src/pipeline.py --fred-api-key $FRED_API_KEY
```

Or run specific steps:
```bash
# Skip external data fetching
python src/pipeline.py --skip-external

# Skip Comtrade processing
python src/pipeline.py --skip-comtrade

# Skip adding indicators
python src/pipeline.py --skip-indicators
```

### 4. Train Models & Generate Forecast

Open the main modeling notebook:
```bash
jupyter notebook notebooks/SABLE_model_training.ipynb
```

Or use the forecast script:
```bash
python src/forecast.py --output outputs/forecasts/submission.csv
```

### 5. Validate & Evaluate

```bash
# Validate submission format
bash scripts/validate_submission.sh outputs/forecasts/submission.csv

# Evaluate against ground truth (when available)
bash scripts/evaluate_submission.sh \
  outputs/forecasts/submission.csv \
  inputs/reference/oct2025_truth.csv
```

---

## 📋 Data Processing Pipeline Details

### Step 1: Process Main Trade Data (2023-2024)

Processes OEC trade data for USA and China:
- Aggregate product IDs to HS4 level (first 4 digits)
- Calculate number of unique products per country-month
- Filter countries with ≥200 products (challenge requirement)
- Add product names from HS4 code mappings

**Module**: `src/data_processing/process_trade_data.py`

### Step 2: Fetch External Data

Retrieves economic data from external APIs:
- **Exchange Rates**: Monthly USD rates for all currencies (Frankfurter API)
- **Commodity Prices**: Energy, metals, agriculture prices (FRED API)

**Module**: `src/data_processing/external_data.py`

### Step 3: Process Comtrade Data (2021, 2022, 2025)

Processes additional UN Comtrade datasets:
- Merge monthly files by year and trade flow
- Handle encoding issues and missing columns
- Normalize to standard format
- Filter by quantity thresholds

**Module**: `src/data_processing/comtrade_processor.py`

### Step 4: Add Economic Indicators

Integrates macroeconomic indicators:
- **GDP Components**: Final consumption, capital formation, inventories
- **REER**: Real Effective Exchange Rate (IMF data)
- Merge with trade data by country and month

**Module**: `src/data_processing/indicators.py`

---

## 🔧 Configuration

All paths and parameters are centralized in `configs/config.yaml`:

- **Paths**: Input/output directories
- **Data Processing**: Minimum products threshold, date ranges, file names
- **Model**: Feature categories, target variable, validation split
- **Submission**: Required columns, validation rules

Edit this file to customize the pipeline behavior.

---

## 📈 Model Training

Our modeling approach uses ensemble methods:

1. **Feature Engineering**
   - Temporal features: month trends, seasonality
   - Categorical encoding: target encoding for countries/products
   - Economic indicators: normalized and lagged features
   - Interaction features: country×product, country×month

2. **Model Architecture**
   - Primary: CatBoost (handles categorical features natively)
   - Ensemble: XGBoost, LightGBM, RandomForest
   - Stacking: Meta-learner combines predictions

3. **Validation Strategy**
   - Time-based split: Last 6 months for validation
   - Cross-validation: By country and product groups
   - Metric: sMAPE (official competition metric)

See `notebooks/SABLE_model_training.ipynb` for full details.

---

## 📝 Submission Format

Submissions must be CSV files with columns:
```
"Country1","Country2","ProductCode","TradeFlow","Value"
```

Example:
```csv
"USA","CHL","8404","Export","1234567"
"USA","CHN","8405","Import","9876543"
"CHN","USA","8404","Export","5555555"
```

- **Country1, Country2**: ISO-3 codes (e.g., USA, CHN, DEU)
- **ProductCode**: 4-digit HS4 code
- **TradeFlow**: "Export" or "Import"
- **Value**: Trade value in USD (non-negative)

Use `src/validate_submission.py` to check format before submitting.

---

## 🧪 Testing

Run unit tests:
```bash
python -m pytest tests/
```

Test specific module:
```bash
python -m pytest tests/test_metrics.py
```

---

## 📚 Documentation

- **Challenge Details**: [`docs/challenge_details.md`](docs/challenge_details.md)
- **Data Pipeline**: Documentation of each processing step
- **Notebooks**: Analysis and modeling documentation in Jupyter notebooks
- **API Reference**: Docstrings in all Python modules

---

## 🤝 Team & Contribution

**Team SABLE** — AI4Trade Global Challenge 2025

### Project Structure Notes

- **Inputs**: Not version controlled (add to `.gitignore`). Keep data local.
- **Outputs**: Generated artifacts, not version controlled.
- **Legacy Files**: `1_data_processing.py` and `2_rajout_donnees_externes.py` are legacy scripts. Use the modular `src/data_processing/` modules instead.

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OEC** (Observatory of Economic Complexity) for trade data
- **CCL** (Center for Collective Learning) for organizing the challenge
- **World Bank** for economic indicators
- **IMF** for REER data
- **FRED** for commodity price data

---

## 📞 Contact & Links

- **Challenge Website**: [Link to challenge page]
- **OEC Platform**: https://oec.world/
- **Documentation**: See `docs/` folder
- **Issues**: Use GitHub Issues for questions/bugs

---

**Good luck with the challenge! 🚀**
