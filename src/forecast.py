from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import yaml


def load_config() -> dict:
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def naive_latest_baseline(training_data_path: Optional[Path]) -> pd.DataFrame:
    """Return a trivial baseline if training data exists.

    Expected training schema (flexible): must include the 5 required submission columns
    plus some date indicator (e.g., Year, Month or a 'Date' column). We simply take the
    latest available month as the forecast.
    """
    if training_data_path is None or not training_data_path.exists():
        # Return an empty DataFrame with the required columns
        return pd.DataFrame(
            columns=["Country1", "Country2", "ProductCode", "TradeFlow", "Value"]
        ).astype(
            {
                "Country1": str,
                "Country2": str,
                "ProductCode": str,
                "TradeFlow": str,
                "Value": float,
            }
        )

    df = pd.read_csv(training_data_path)
    required_cols = ["Country1", "Country2", "ProductCode", "TradeFlow", "Value"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Training data missing required columns {missing}")

    # Try to detect a time dimension
    time_cols = [c for c in ("Year", "Month", "Date") if c in df.columns]
    if not time_cols:
        # No time info, return last observed rows as-is
        return df[required_cols].copy()

    # Heuristic: sort by Year, then Month if present, or Date
    if "Date" in time_cols:
        df_sorted = df.sort_values("Date")
    else:
        sort_cols = [c for c in ("Year", "Month") if c in df.columns]
        df_sorted = df.sort_values(sort_cols)

    latest_group = df_sorted.groupby(
        ["Country1", "Country2", "ProductCode", "TradeFlow"], as_index=False
    ).tail(1)
    return latest_group[required_cols].copy()


def main() -> None:
    cfg = load_config()
    forecasts_dir = Path(cfg["paths"]["forecasts"])
    forecasts_dir.mkdir(parents=True, exist_ok=True)

    # Optional: put your training file path here
    training_csv = None  # e.g., Path("inputs/processed/training_panel.csv")
    submission = naive_latest_baseline(training_csv)

    out_path = forecasts_dir / "submission.csv"
    submission.to_csv(out_path, index=False)
    print(f"Wrote baseline submission to {out_path}")


if __name__ == "__main__":
    main()
