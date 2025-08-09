import numpy as np

from src.metrics import compute_smape


def test_smape_zero_error():
    y = np.array([1.0, 2.0, 3.0])
    assert compute_smape(y, y) == 0.0


def test_smape_symmetric_small_case():
    y = np.array([100.0])
    yhat = np.array([110.0])
    # |100-110|/(|100|+|110|) = 10/210; sMAPE = 200 * (10/210) ≈ 9.5238
    smape = compute_smape(y, yhat)
    assert abs(smape - 9.5238) < 1e-3


def test_smape_handles_zeros():
    y = np.array([0.0, 0.0, 10.0])
    yhat = np.array([0.0, 5.0, 0.0])
    smape = compute_smape(y, yhat)
    # term0=0, term1=5/5=1, term2=10/10=1 -> mean=2/3; sMAPE=200*(2/3)=133.33
    assert abs(smape - 133.3333) < 1e-2
