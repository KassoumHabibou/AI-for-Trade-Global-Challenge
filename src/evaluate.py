from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from .metrics import compute_smape


def load_config() -> dict:
    cfg_path = Path("configs/config.yaml")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def evaluate_submission(
    submission_path: Path, truth_path: Path, output_dir: Path
) -> dict:
    cfg = load_config()
    required_cols = cfg["submission"]["required_columns"]

    submission = load_csv(submission_path)
    truth = load_csv(truth_path)

    missing_cols = [c for c in required_cols if c not in submission.columns]
    if missing_cols:
        raise ValueError(f"Submission is missing required columns: {missing_cols}")

    # Join on the key columns
    key_cols = [c for c in required_cols if c != "Value"]
    merged = truth.merge(
        submission[key_cols + ["Value"]].rename(columns={"Value": "Predicted"}),
        on=key_cols,
        how="left",
        validate="one_to_one",
    )

    if merged["Predicted"].isna().any():
        n_missing = int(merged["Predicted"].isna().sum())
        raise ValueError(
            f"Submission is missing {n_missing} predictions matching the truth keys"
        )

    score = compute_smape(merged["Value"], merged["Predicted"])  # type: ignore[arg-type]
    result = {"metric": cfg["evaluation"]["metric"], "score": score}

    output_dir.mkdir(parents=True, exist_ok=True)
    score_path = output_dir / "score.json"
    with score_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate submission via sMAPE")
    parser.add_argument(
        "--submission", type=Path, required=True, help="Path to submission CSV"
    )
    parser.add_argument(
        "--truth", type=Path, required=True, help="Path to ground-truth CSV"
    )
    args = parser.parse_args()

    cfg = load_config()
    result = evaluate_submission(
        submission_path=args.submission,
        truth_path=args.truth,
        output_dir=Path(cfg["paths"]["evaluation"]),
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
