from __future__ import annotations

import numpy as np
import pandas as pd


def compute_smape(
    true_values: pd.Series | np.ndarray, predicted_values: pd.Series | np.ndarray
) -> float:
    """Compute symmetric Mean Absolute Percentage Error (sMAPE) in percent.

    sMAPE = 100% * (2/n) * sum(|y - ŷ| / (|y| + |ŷ|))

    Handles zeros robustly; when denominator is zero for a pair, that term contributes 0.

    Parameters
    ----------
    true_values: array-like of shape (n_samples,)
    predicted_values: array-like of shape (n_samples,)

    Returns
    -------
    float
        sMAPE in percentage points (0–200]
    """
    y_true = np.asarray(true_values, dtype=float)
    y_pred = np.asarray(predicted_values, dtype=float)

    if y_true.shape != y_pred.shape:
        raise ValueError("true_values and predicted_values must have the same shape")

    numerator = np.abs(y_true - y_pred)
    denominator = np.abs(y_true) + np.abs(y_pred)
    # Avoid division by zero: where denom is zero, contribution is zero
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.divide(
            numerator, denominator, out=np.zeros_like(numerator), where=denominator != 0
        )
    smape = 200.0 * np.mean(terms)
    return float(smape)
