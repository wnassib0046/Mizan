"""The science core.

Main test:  Seasonal Mann-Kendall on the monthly series (each calendar month is
            compared only with itself, so the seasons cannot fake a trend).
Size:       Sen's slope on the annual values, with a 95% confidence interval.
Robustness: Hamed-Rao Mann-Kendall (corrects for autocorrelation) and ordinary
            least squares on the annual values. Robust = all three agree.
"""
import math

import numpy as np
import pandas as pd
import pymannkendall as mk
from scipy import stats

import config


def _clean_p(p) -> float | None:
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return None
    return float(p)


def analyze_trend(monthly: pd.DataFrame, annual: pd.DataFrame, alpha: float = config.ALPHA) -> dict:
    """monthly: columns date, value (complete, regular months)
    annual:  columns year, value"""
    if len(annual) < 3:
        raise ValueError("not enough years for a trend")

    # 1. Seasonal Kendall on monthly values
    sk = mk.seasonal_test(monthly["value"].to_numpy(), period=12, alpha=alpha)
    sk_p = _clean_p(sk.p)

    years = annual["year"].to_numpy(dtype=float)
    vals = annual["value"].to_numpy(dtype=float)

    # 2. Sen's slope + 95% interval on annual values
    ts = stats.theilslopes(vals, years, alpha=1 - alpha)
    slope, intercept, lo, hi = ts[0], ts[1], ts[2], ts[3]

    # 3a. Hamed-Rao modified Mann-Kendall on annual values
    hr = mk.hamed_rao_modification_test(vals, alpha=alpha)
    hr_p = _clean_p(hr.p)

    # 3b. OLS on annual values
    ols = stats.linregress(years, vals)
    ols_p = _clean_p(ols.pvalue)

    if sk_p is not None and sk_p < alpha:
        direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "no_trend"
    else:
        direction = "no_trend"

    sign = np.sign(slope)
    methods_agree = bool(
        sk_p is not None and sk_p < alpha
        and hr_p is not None and hr_p < alpha
        and ols_p is not None and ols_p < alpha
        and np.sign(ols.slope) == sign and sign != 0
    )

    y0, y1 = int(years.min()), int(years.max())
    return {
        "method": "Seasonal Kendall + Sen's slope",
        "direction": direction,
        "p_value": round(sk_p, 4) if sk_p is not None else None,
        "slope_per_decade": round(float(slope) * 10, 3),
        "ci95": [round(float(lo) * 10, 3), round(float(hi) * 10, 3)],
        "change_over_period": round(float(slope) * (y1 - y0), 3),
        "line": [
            {"year": y0, "value": round(float(intercept + slope * y0), 3)},
            {"year": y1, "value": round(float(intercept + slope * y1), 3)},
        ],
        "robustness": {
            "hamed_rao_p": round(hr_p, 4) if hr_p is not None else None,
            "ols_p": round(ols_p, 4) if ols_p is not None else None,
            "ols_slope_per_decade": round(float(ols.slope) * 10, 3),
            "methods_agree": methods_agree,
        },
    }
