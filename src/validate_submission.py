from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml


def load_config() -> dict:
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_schema(df: pd.DataFrame, cfg: dict) -> Dict[str, List[str]]:
    errors: Dict[str, List[str]] = {"errors": [], "warnings": []}
    required = cfg["submission"]["required_columns"]
    trade_flows = set(cfg["submission"]["trade_flow_values"])
    cc_len = int(cfg["submission"]["country_code_len"])
    pc_len = int(cfg["submission"]["product_code_len"])

    # Columns present
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors["errors"].append(f"Missing required columns: {missing}")
        return errors

    # Basic type checks
    if df["Value"].isna().any():
        errors["errors"].append("Column 'Value' contains missing values")
    if (df["Value"] < 0).any():
        errors["errors"].append("Column 'Value' contains negative values")

    # TradeFlow constraints
    bad_tf = ~df["TradeFlow"].isin(trade_flows)
    if bad_tf.any():
        unique_bad = sorted(df.loc[bad_tf, "TradeFlow"].astype(str).unique().tolist())
        errors["errors"].append(
            f"Invalid TradeFlow values: {unique_bad}. Allowed: {sorted(trade_flows)}"
        )

    # Country codes: ISO-3, uppercase letters (loosely validated)
    iso3_pattern = re.compile(r"^[A-Z]{3}$")
    for col in ("Country1", "Country2"):
        bad_cc = ~df[col].astype(str).str.fullmatch(iso3_pattern)
        if bad_cc.any():
            errors["errors"].append(
                f"Column '{col}' has invalid ISO-3 codes (must be A-Z uppercase, length {cc_len})"
            )

    # Product codes: HS4 numeric, 4 digits
    hs4_pattern = re.compile(r"^[0-9]{%d}$" % pc_len)
    bad_pc = ~df["ProductCode"].astype(str).str.fullmatch(hs4_pattern)
    if bad_pc.any():
        errors["errors"].append(
            f"Column 'ProductCode' must be exactly {pc_len} digits (HS4)"
        )

    # Duplicate keys check
    key_cols = [c for c in required if c != "Value"]
    dup_idx = df.duplicated(subset=key_cols, keep=False)
    if dup_idx.any():
        num_dup = int(dup_idx.sum())
        errors["errors"].append(
            f"Duplicate rows for key columns {key_cols}: {num_dup} duplicates detected"
        )

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate AI4Trade submission file")
    parser.add_argument(
        "--file", type=Path, required=True, help="Path to submission CSV to validate"
    )
    args = parser.parse_args()

    cfg = load_config()
    df = pd.read_csv(args.file)
    report = validate_schema(df, cfg)

    out_dir = Path(cfg["paths"]["evaluation"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "validation.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if report["errors"]:
        print("Validation FAILED. See outputs/evaluation/validation.json for details.")
    else:
        print("Validation PASSED.")


if __name__ == "__main__":
    main()
