## AI for Trade Global Challenge — Team Repository Template

This repository is a ready-to-use, best-practice template to participate in the AI for Trade Global Challenge organized by the Center for Collective Learning (CCL) with the Observatory of Economic Complexity (OEC) and partners. It is designed to be easily replicable by teams and reviewers, with a clear structure for inputs, code, and outputs, plus scripts to validate and evaluate your forecast submission.

### Purpose of the Challenge
- **Goal**: Submit a forecast of trade flows for the United States and China for October 2025.
- **Deliverable**: A CSV with predictions for trade values in USD for the top 20 sources and destinations that trade at least 200 HS4 products with the US and China, for both exports and imports.
- **Evaluation**: Predictions will be evaluated using sMAPE (symmetric mean absolute percentage error) against the official data each country publishes.

Key dates, eligibility, methods, submission format, and prizes are summarized below (full details in `docs/challenge_details.md`).

### Key Dates
- Submissions due: **Oct 31, 2025 (CET, midnight)**
- Evaluation: Once October 2025 data is published (likely December 2025)

### Eligibility (abridged)
- Open globally to academics, professionals, students, and independent researchers
- Teams of 1–5 members (single submission per participant)
- Must register to access training data from OEC
- OEC/CCL staff are not eligible

### Allowed Methods
Any method is allowed (econometric models, ML/DL, hybrids, ensembles, domain heuristics). The only requirement is that your output must match the submission format described below.

### Submission Format (CSV)
Columns (quoted): `"Country1","Country2","ProductCode","TradeFlow","Value"`
- `Country1`, `Country2`: ISO-3 codes
- `ProductCode`: HS4 code (4 digits)
- `TradeFlow`: `Export` or `Import`
- `Value`: trade value in USD (non-negative numeric)

Example rows:
```
"USA","CHL","8404","Export","1234567"
"USA","CHN","8405","Import","1234567"
```

### Prizes (abridged)
- 1st: 3000 USD + 1-year OEC Premium for all members
- 2nd: 2000 USD + 1-year OEC Premium for all members
- 3rd: 1000 USD + 1-year OEC Premium for all members

Partners include: OEC, World Bank Trade Practice, ADB, ELIAS, Cambridge Supply Chain AI Lab, INET Oxford, MIOIR (AMBS), CIAS (Corvinus), IAST (TSE), Fundación Cotec, UC Berkeley Global Opportunity Lab. See `docs/challenge_details.md` for full context.

---

## Repository Organization

This layout follows data science best practices (inspired by Cookiecutter Data Science), adapted to the challenge’s input/output workflow:

```
.
├── README.md                       # Start here: purpose, structure, quickstart
├── LICENSE                         # MIT by default (update if needed)
├── requirements.txt                # Python dependencies for reproducibility
├── Makefile                        # Common commands (setup, test, evaluate, etc.)
├── configs/
│   └── config.yaml                 # Centralized configuration (paths, columns)
├── docs/
│   └── challenge_details.md        # Full challenge description and rules
├── inputs/                         # Input data (not versioned; keep small refs)
│   ├── raw/                        # Raw provided data (e.g., OEC training data)
│   ├── external/                   # Any extra data sources
│   └── reference/                  # Lookups, code lists, metadata
├── outputs/                        # All generated artifacts (ignored by git)
│   ├── interim/                    # Intermediate data
│   ├── processed/                  # Cleaned/engineered datasets
│   ├── forecasts/                  # Final forecast CSVs ready to submit
│   ├── evaluation/                 # Scores, validation reports
│   └── reports/                    # Figures, tables, writeups
├── submissions/
│   ├── template_submission.csv     # Example with required header
│   └── README.md                   # How to produce and validate submissions
├── src/                            # Python source code (install-free runnable)
│   ├── __init__.py
│   ├── metrics.py                  # sMAPE and other metrics
│   ├── validate_submission.py      # Schema checks for the CSV
│   ├── evaluate.py                 # Compute sMAPE given truth vs submission
│   └── forecast.py                 # Baseline stub to produce a CSV
├── scripts/                        # Convenience shell scripts
│   ├── make_submission.sh          # Run baseline to create a CSV
│   ├── validate_submission.sh      # Validate a CSV against the schema
│   └── evaluate_submission.sh      # Evaluate a CSV against ground truth
├── tests/
│   └── test_metrics.py             # Unit test for sMAPE
└── notebooks/                      # Exploratory analysis, modeling
    └── README.md                   # Guidance for notebooks
```

Notes:
- `inputs/` and `outputs/` are intentionally outside version control (except light placeholders) to keep the repo small and privacy-safe.
- Use `configs/config.yaml` to centralize paths and column names.
- Use `scripts/` and `Makefile` targets to ensure repeatability.

---

## Quickstart

### 1) Environment
Requirements: Python 3.10+ (3.11/3.12 recommended)

```bash
# From the repository root
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

### 2) Prepare data
- Download OEC training data for US and China (months in 2023–2024) and place them under `inputs/raw/`.
- Any extra lookups or code lists go under `inputs/reference/`.

### 3) Produce a baseline submission
```bash
bash scripts/make_submission.sh
# Result: outputs/forecasts/submission.csv
```

### 4) Validate the submission locally
```bash
bash scripts/validate_submission.sh outputs/forecasts/submission.csv
# Report: outputs/evaluation/validation.json
```

### 5) Evaluate (when truth is available)
```bash
bash scripts/evaluate_submission.sh \
  outputs/forecasts/submission.csv \
  inputs/reference/oct2025_truth.csv
# Score: outputs/evaluation/score.json
```

---

## Submission Guidelines (recap)
- File: plain-text CSV (UTF-8), due by Oct 31, 2025 (CET, midnight)
- Columns: `Country1,Country2,ProductCode,TradeFlow,Value`
- Countries: ISO-3 codes; Products: HS4 codes (4 digits); TradeFlow: `Export` or `Import`; Values in USD
- Include a two-page method description (math and reproducibility encouraged)
- Top-3 teams present methods in an online ceremony

See `submissions/README.md` for tips and `src/validate_submission.py` for programmatic checks.

---

## Evaluation
- Official metric: **sMAPE** (symmetric Mean Absolute Percentage Error)
- Provided here: `src/metrics.py` and `src/evaluate.py`

To be prize-eligible, your forecast must beat a simple baseline that uses the latest raw trade data available at the time of submission. You can prototype your own baselines using `src/forecast.py`.

---

## Reproducibility
- Dependencies pinned in `requirements.txt`
- Centralized configuration in `configs/config.yaml`
- Deterministic utilities where applicable; set seeds in your own modeling code
- Keep heavy data out of version control; document sources under `docs/` and `inputs/reference/`

---

## License and Attribution
- Default license: MIT (see `LICENSE`). Adjust if your organization requires otherwise.
- If you publish results, please cite the AI for Trade Global Challenge and the OEC/CCL data sources appropriately.

---

## Acknowledgments
This template was created to help teams focus on modeling while maintaining clarity, reproducibility, and smooth handoffs among collaborators.

