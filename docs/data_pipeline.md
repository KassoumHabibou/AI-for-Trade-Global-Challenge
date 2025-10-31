# Data Processing Pipeline Documentation

This document provides detailed information about each stage of the AI4Trade data processing pipeline.

## Overview

The pipeline transforms raw trade data and external economic data into a unified dataset suitable for forecasting. It consists of four main stages:

```
Raw Data → Process Trade Data → Add External Data → Process Comtrade → Add Indicators → Model-Ready Data
```

---

## Stage 1: Process Main Trade Data (2023-2024)

### Purpose
Process OEC trade data for USA and China (2023-2024) to create clean, aggregated datasets at HS4 level.

### Input Files
- `inputs/raw/ForParticipants/trade_s_usa_state_m_hs_2023.csv`
- `inputs/raw/ForParticipants/trade_s_usa_state_m_hs_2024.csv`
- `inputs/raw/ForParticipants/trade_s_chn_m_hs_2023.csv`
- `inputs/raw/ForParticipants/trade_s_chn_m_hs_2024.csv`
- `inputs/reference/code_hs4.xlsx` (HS4 product code mappings)

### Processing Steps

1. **Load HS4 Mappings**
   - Read Excel file with HS4 code to product name mappings
   - Create dictionary for fast lookup

2. **Aggregate to HS4 Level**
   - Extract first 4 digits of product_id as product_id_hs4
   - Group by: month_id, trade_flow_name, country_id, country_name, product_id_hs4
   - Sum trade_value within each group

3. **Calculate Product Diversity**
   - Count unique products (product_id_hs4) per country-month
   - Store as `nb_product` column
   - This measures how diversified a country's trade portfolio is

4. **Filter Countries**
   - Keep only countries with `nb_product > 200`
   - This is a challenge requirement: focus on countries trading ≥200 HS4 products
   - Ensures sufficient data quality for modeling

5. **Add Product Names**
   - Map product_id_hs4 to human-readable product names
   - Add as `product_name_hs4` column

### Output Files
- `outputs/processed/USA_2023_finale.csv`
- `outputs/processed/USA_2024_finale.csv`
- `outputs/processed/china_2023_finale.csv`
- `outputs/processed/china_2024_finale.csv`

### Output Schema
```
month_id              : int     - YYYYMM format (e.g., 202301)
trade_flow_name       : str     - "Imports" or "Exports"
country_id            : str     - ISO-3 country code (e.g., "DEU")
country_name          : str     - Country name (e.g., "Germany")
product_id_hs4        : str     - 4-digit HS code (e.g., "8404")
trade_value           : float   - Trade value in USD
nb_product            : int     - Number of unique products for this country-month
product_name_hs4      : str     - Product description
```

### Module
`src/data_processing/process_trade_data.py`

---

## Stage 2: Fetch and Merge External Data

### Purpose
Enrich trade data with external economic variables that may influence trade flows.

### 2.1 Exchange Rates

**Source**: [Frankfurter API](https://www.frankfurter.app/)  
**Description**: Daily exchange rates from European Central Bank  
**Coverage**: 30+ currencies vs USD

**Processing**:
1. Query API for end-of-month rates for each month in range
2. Convert to monthly frequency (last trading day of month)
3. Create `month_id_join` column (next month's ID) for lagged merge
4. Save intermediate result

**Output**: `outputs/interim/exchange_rates.csv`

**Columns**:
```
[Currency columns]: EUR, GBP, JPY, CNY, etc.
month_id_join     : int - YYYYMM of next month
```

### 2.2 Commodity Prices

**Source**: [FRED API](https://fred.stlouisfed.org/) (Federal Reserve Economic Data)  
**API Key Required**: Yes (free registration)

**Coverage**:
- **Energy**: WTI Crude Oil, Brent Oil, Natural Gas
- **Metals**: Copper, Aluminum, Nickel, Zinc, Tin, Lead, Iron Ore
- **Agriculture**: Wheat, Corn, Soybeans, Rice, Coffee, Cocoa, Sugar, Cotton

**Processing**:
1. Fetch daily/monthly series from FRED
2. Resample to monthly frequency (last value of month)
3. Create `month_id_join` column for lagged merge
4. Save intermediate result

**Output**: `outputs/interim/commodity_prices.csv`

**Columns**:
```
Crude Oil (WTI)     : float - USD per barrel
Brent Oil           : float - USD per barrel
Copper              : float - USD per metric ton
Wheat               : float - USD per metric ton
[etc.]
month_id_join       : int - YYYYMM of next month
```

### 2.3 Merge with Trade Data

**Logic**: 
- Merge based on `month_id` (trade data) = `month_id_join` (external data)
- This creates a **lagged** merge: trade in month M uses prices from month M-1
- Rationale: Economic data from previous month affects current month's trade

**Output**: `outputs/processed/with_external/[filename]_vf.csv`

### Module
`src/data_processing/external_data.py`

---

## Stage 3: Process Comtrade Data (2021, 2022, 2025)

### Purpose
Process additional UN Comtrade monthly HS4 data to extend the historical training window.

### Input Files
Multiple monthly CSV files in format:
- `inputs/raw/comtrade_monthly_hs4_outputs/USA_M_YYYYMM_HS4.csv` (imports)
- `inputs/raw/comtrade_monthly_hs4_outputs/USA_X_YYYYMM_HS4.csv` (exports)
- Similar for China (CHN)

### Processing Steps

#### 3.1 Merge Monthly Files

1. **Find Files**: Glob pattern matching for year and trade type
2. **Handle Encoding Issues**: Try multiple encodings (latin-1, utf-8, etc.)
3. **Fix Column Mismatches**: Add placeholder names if data columns > header columns
4. **Filter by Quantity**: Keep rows where `qty >= 0`
5. **Concatenate**: Merge all months into single file per year-country-flow

**Output**: `outputs/interim/comtrade_merged/USA_2021_import.csv`, etc.

#### 3.2 Normalize Column Names

Map Comtrade column names to standard schema:
```
period        → month_id
flowDesc      → trade_flow_name
partnerISO    → country_id
partnerDesc   → country_name
cmdCode       → product_id_hs4
primaryValue  → trade_value
qty           → quantity
cmdDesc       → product_name_hs4
```

#### 3.3 Calculate nb_product

Count unique products per country-month (same as Stage 1)

#### 3.4 Filter Countries

Keep only countries with `nb_product > 200`

**Output**: `outputs/processed/comtrade_final/USA_2021_import_final.csv`, etc.

### Module
`src/data_processing/comtrade_processor.py`

---

## Stage 4: Add Economic Indicators

### Purpose
Integrate macroeconomic indicators (GDP, REER) that capture country-level economic conditions.

### 4.1 GDP and Macroeconomic Indicators

**Source**: World Bank, OECD (provided in `df_long.csv`)

**Coverage**:
- Gross Domestic Product (GDP)
- Final consumption expenditure
- Gross capital formation
- Changes in inventories

**Filters**:
- Price Type: "Constant prices" (inflation-adjusted)
- Seasonal Adjustment: "Seasonally adjusted (SA)"

**Processing**:
1. Filter indicators by keywords (GDP, consumption, capital, inventories)
2. Filter by price type and seasonal adjustment
3. Pivot from long to wide format (one column per indicator)
4. Create standardized column names:
   - `gdp_constant_sa`
   - `final_consumption_constant_sa`
   - `gross_capital_formation_constant_sa`
   - `changes_inventories_constant_sa`

**Output Schema** (wide format):
```
country_id                          : str   - ISO-3 code
month_id                            : int   - YYYYMM
gdp_constant_sa                     : float - GDP in constant prices
final_consumption_constant_sa       : float
gross_capital_formation_constant_sa : float
changes_inventories_constant_sa     : float
```

### 4.2 REER (Real Effective Exchange Rate)

**Source**: IMF (provided in `EER_COUNTRIES.csv`)

**Description**: 
- REER measures a country's currency strength relative to a basket of other currencies
- Adjusted for inflation differences
- Index base year: 2010 = 100

**Processing**:
1. Filter for REER indicator
2. Extract date columns (format: "2021-M01", "2021-M02", etc.)
3. Melt from wide to long format
4. Convert period format: "2021-M01" → 202101
5. Remove missing values

**Output Schema**:
```
country_id  : str   - ISO-3 code
month_id    : int   - YYYYMM
REER        : float - REER index value
```

### 4.3 Merge with Trade Data

**Merge Logic**:
- Join on: `[country_id, month_id]`
- Type: Left join (keep all trade data rows)
- Result: Trade data with added indicator columns

**Output**: `outputs/processed/with_indicators/[filename]_Additional.csv`

### Module
`src/data_processing/indicators.py`

---

## Final Dataset Schema

After all stages, the complete dataset includes:

### Core Trade Variables
- `month_id`: Time identifier (YYYYMM)
- `trade_flow_name`: "Imports" or "Exports"
- `country_id`: ISO-3 country code
- `country_name`: Country name
- `product_id_hs4`: 4-digit HS code
- `product_name_hs4`: Product description
- `trade_value`: Trade value in USD (target variable)
- `quantity`: Trade quantity
- `nb_product`: Product diversity measure

### Exchange Rates (30+ columns)
- `EUR`, `GBP`, `JPY`, `CNY`, etc.

### Commodity Prices (~18 columns)
- `Crude Oil (WTI)`, `Brent Oil`, `Natural Gas`
- `Copper`, `Aluminum`, `Nickel`, etc.
- `Wheat`, `Corn`, `Soybeans`, etc.

### Economic Indicators (4+ columns)
- `gdp_constant_sa`
- `final_consumption_constant_sa`
- `gross_capital_formation_constant_sa`
- `changes_inventories_constant_sa`

### REER (1 column)
- `REER`: Real Effective Exchange Rate index

---

## Running the Pipeline

### Complete Pipeline

```bash
python src/pipeline.py --fred-api-key YOUR_API_KEY
```

### Skip Specific Stages

```bash
# Skip external data fetching
python src/pipeline.py --skip-external

# Skip Comtrade processing
python src/pipeline.py --skip-comtrade

# Skip adding indicators
python src/pipeline.py --skip-indicators
```

### Custom Configuration

Edit `configs/config.yaml` to customize:
- Input/output paths
- Date ranges
- Minimum product threshold
- Years to process
- Feature categories

---

## Troubleshooting

### Common Issues

1. **Missing Files**
   - Ensure all input files are in correct directories
   - Check file names match configuration

2. **API Errors**
   - Frankfurter API: Check internet connection, API may have rate limits
   - FRED API: Verify API key is valid and active

3. **Encoding Issues**
   - Comtrade files use various encodings (latin-1, utf-8)
   - Pipeline tries multiple encodings automatically

4. **Memory Issues**
   - Processing large Comtrade files may require 8GB+ RAM
   - Consider processing years separately if needed

5. **Missing Indicators**
   - Not all countries have complete indicator coverage
   - Left join ensures trade data is preserved even when indicators are missing
   - Models should handle missing values appropriately

---

## Performance Considerations

**Processing Time**:
- Stage 1 (Trade Data): ~2-5 minutes
- Stage 2 (External Data): ~5-10 minutes (depends on API)
- Stage 3 (Comtrade): ~10-20 minutes (large files)
- Stage 4 (Indicators): ~5-10 minutes

**Total Pipeline**: ~30-45 minutes

**Optimization Tips**:
- Cache external data (exchange rates, commodities) to avoid repeated API calls
- Process Comtrade years in parallel if possible
- Use SSD storage for faster I/O

---

## Data Quality Checks

Built-in quality checks:
- ✅ Filter countries with insufficient products (nb_product ≤ 200)
- ✅ Remove rows with negative quantities
- ✅ Validate column names and types
- ✅ Check for duplicate rows
- ✅ Handle missing values in indicators (left join)

Recommended additional checks:
- [ ] Check for outliers in trade values
- [ ] Validate country-product combinations
- [ ] Check temporal consistency (no gaps in time series)
- [ ] Verify exchange rate sanity (reasonable ranges)
- [ ] Compare aggregated totals with official statistics

---

## Next Steps

After running the pipeline:

1. **Exploratory Analysis**: See `notebooks/exploratory_analysis.ipynb`
2. **Feature Engineering**: Create additional features for modeling
3. **Model Training**: See `notebooks/SABLE_model_training.ipynb`
4. **Forecasting**: Generate October 2025 predictions
5. **Validation**: Check submission format and evaluate

---

## References

- [HS Classification](https://www.wcoomd.org/en/topics/nomenclature/overview/what-is-the-harmonized-system.aspx)
- [Frankfurter API Docs](https://www.frankfurter.app/docs/)
- [FRED API Docs](https://fred.stlouisfed.org/docs/api/fred/)
- [OEC Platform](https://oec.world/)

