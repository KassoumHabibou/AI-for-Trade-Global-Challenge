# Notebooks Directory

This directory contains Jupyter notebooks for exploratory analysis, data processing, and model training.

## 📓 Available Notebooks

### 1. `SABLE_12_model_training.ipynb`
**Purpose**: Main model training and forecasting notebook

**Contents**:
- Data loading and preprocessing
- Feature engineering
- Model training (ensemble methods)
- Model evaluation and validation
- Forecast generation for October 2025

**Requirements**:
- Processed data from pipeline (outputs/processed/)
- CatBoost, XGBoost, LightGBM installed
- FRED API key for commodity data

**Usage**:
```bash
jupyter notebook notebooks/SABLE_12_model_training.ipynb
```

---

### 2. `comtrade_data_processing.ipynb`
**Purpose**: Processing and analysis of UN Comtrade data

**Contents**:
- Loading and merging monthly Comtrade files
- Handling encoding issues and missing columns
- Splitting data by year and trade flow
- Column normalization and renaming
- Adding economic indicators (GDP, REER)

**Note**: This notebook documents the Comtrade processing workflow. The logic has been extracted to `src/data_processing/comtrade_processor.py` for production use.

**Usage**:
```bash
jupyter notebook notebooks/comtrade_data_processing.ipynb
```

---

### 3. `exploratory_analysis.ipynb` (Template)
**Purpose**: Exploratory data analysis

**Recommended analyses**:
- Trade flow distributions
- Country-product combinations
- Temporal trends and seasonality
- Missing data patterns
- Correlation analysis
- Feature importance exploration

**Create from template**:
```python
# Basic EDA structure
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load processed data
df = pd.read_csv("outputs/processed/USA_2023_finale.csv")

# Your analysis here...
```

---

## 🚀 Getting Started

### 1. Start Jupyter

From repository root:
```bash
# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Start Jupyter
jupyter notebook
```

This will open Jupyter in your browser at `http://localhost:8888`

### 2. Set Up Notebook Environment

Add this to the top of each notebook:
```python
import sys
sys.path.append('..')  # Add src/ to path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure display
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
plt.style.use('seaborn-v0_8-darkgrid')
%matplotlib inline

# Load configuration
import yaml
with open('../configs/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

### 3. Access Processed Data

```python
from pathlib import Path

# Define paths from config
processed_dir = Path(config['paths']['processed'])

# Load data
usa_2023 = pd.read_csv(processed_dir / "USA_2023_finale.csv")
usa_2024 = pd.read_csv(processed_dir / "USA_2024_finale.csv")
china_2023 = pd.read_csv(processed_dir / "china_2023_finale.csv")
china_2024 = pd.read_csv(processed_dir / "china_2024_finale.csv")
```

---

## 📝 Best Practices

### Notebook Organization

1. **Clear Structure**
   ```
   # Title and Description
   ## 1. Setup (imports, config)
   ## 2. Load Data
   ## 3. Analysis/Processing
   ## 4. Results/Conclusions
   ## 5. Export (if applicable)
   ```

2. **Use Markdown**
   - Document your reasoning
   - Explain complex code
   - Summarize findings

3. **Restart and Clear Output**
   - Before committing, restart kernel and clear output
   - Ensures reproducibility
   - Reduces file size

### Code Quality

1. **Modular Functions**
   ```python
   # Good: Reusable function
   def calculate_trade_balance(df):
       exports = df[df['trade_flow_name'] == 'Exports']['trade_value'].sum()
       imports = df[df['trade_flow_name'] == 'Imports']['trade_value'].sum()
       return exports - imports
   
   # Use it
   balance = calculate_trade_balance(usa_2023)
   ```

2. **Move Production Code to src/**
   - If code is reusable, move it to `src/` modules
   - Import and use in notebooks
   - Example: Feature engineering functions

3. **Version Control**
   - Notebooks should be committed
   - Clear output before committing (reduces diff noise)
   - Use Git LFS for large notebooks if needed

### Data Loading

1. **Use Relative Paths**
   ```python
   # Good
   data_path = Path("../outputs/processed/USA_2023_finale.csv")
   
   # Avoid
   data_path = "C:/Users/me/AI-for-Trade/outputs/processed/..."
   ```

2. **Check File Existence**
   ```python
   if not data_path.exists():
       print(f"File not found: {data_path}")
       print("Run pipeline first: python src/pipeline.py")
   ```

3. **Memory Management**
   ```python
   # For large files, use chunking
   chunks = pd.read_csv(large_file, chunksize=10000)
   for chunk in chunks:
       process(chunk)
   
   # Or select columns
   df = pd.read_csv(file, usecols=['country_id', 'trade_value'])
   ```

---

## 🔧 Common Tasks

### Task 1: Load All Processed Data

```python
import glob
from pathlib import Path

processed_dir = Path("../outputs/processed")

# Load all finale files
data_files = {}
for file in processed_dir.glob("*_finale.csv"):
    name = file.stem  # Filename without extension
    data_files[name] = pd.read_csv(file)
    print(f"Loaded {name}: {len(data_files[name]):,} rows")
```

### Task 2: Merge Multiple Years

```python
# Combine USA data across years
usa_combined = pd.concat([
    data_files['USA_2023_finale'],
    data_files['USA_2024_finale']
], ignore_index=True)

# Sort by date
usa_combined = usa_combined.sort_values('month_id')
```

### Task 3: Filter for Specific Country

```python
# Get Germany's trade data
germany = usa_combined[usa_combined['country_id'] == 'DEU'].copy()

# Get top trading partners
top_partners = (
    usa_combined.groupby('country_id')['trade_value']
    .sum()
    .sort_values(ascending=False)
    .head(20)
)
```

### Task 4: Visualize Trends

```python
import matplotlib.pyplot as plt

# Trade value over time
monthly_trade = (
    usa_combined.groupby('month_id')['trade_value']
    .sum()
    .reset_index()
)

plt.figure(figsize=(12, 6))
plt.plot(monthly_trade['month_id'], monthly_trade['trade_value'])
plt.title('USA Total Trade Value Over Time')
plt.xlabel('Month')
plt.ylabel('Trade Value (USD)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Task 5: Export Results

```python
# Save analysis results
output_dir = Path("../outputs/reports")
output_dir.mkdir(exist_ok=True)

# Export table
top_partners.to_csv(output_dir / "top_trading_partners.csv")

# Export figure
plt.savefig(output_dir / "trade_trends.png", dpi=300, bbox_inches='tight')
```

---

## 🐛 Troubleshooting

### Issue: Module Not Found

```python
import sys
sys.path.append('..')  # Add parent directory to path

# Now you can import from src/
from src.data_processing import process_trade_data
```

### Issue: Kernel Dies with Large Files

- Reduce chunk size
- Select only needed columns
- Increase available RAM
- Use Dask for out-of-core processing

### Issue: Plots Not Showing

```python
# Add magic command at top of notebook
%matplotlib inline

# Or use
plt.show()
```

---

## 📚 Useful Libraries

### Data Analysis
```python
import pandas as pd
import numpy as np
from scipy import stats
```

### Visualization
```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # Interactive plots
```

### Machine Learning
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
```

### Gradient Boosting
```python
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
```

---

## 🔗 Resources

- [Jupyter Documentation](https://jupyter.org/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)

---

## ✅ Checklist Before Committing

- [ ] Restart kernel and run all cells
- [ ] Clear all output
- [ ] Remove any API keys or secrets
- [ ] Check file paths are relative
- [ ] Add markdown documentation
- [ ] Export important plots/tables to `outputs/reports/`
- [ ] Update this README if adding new notebooks

---

Happy analyzing! 🎉
