"""Synthetic truth tests: put a known slope in, expect the same slope out."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from analysis.trend import analyze_trend  # noqa: E402
from analysis.verdict import make_verdict  # noqa: E402
from processing.clean import clean, completeness  # noqa: E402
from processing.seasonal import annual_values, monthly_anomalies  # noqa: E402


def synthetic(slope_per_year: float, noise: float = 0.3, years=(1981, 2025), seed=0) -> pd.DataFrame:
    """Seasonal cycle + linear trend + noise, monthly."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(f"{years[0]}-01-01", f"{years[1]}-12-01", freq="MS")
    t = (dates.year - years[0]) + (dates.month - 1) / 12
    season = 6 * np.sin(2 * np.pi * (dates.month - 4) / 12)
    values = 18 + season + slope_per_year * t + rng.normal(0, noise, len(dates))
    return pd.DataFrame({"date": dates, "value": values})


def run(df, parameter="T2M"):
    annual = annual_values(df, parameter)
    return analyze_trend(df, annual)


@pytest.mark.parametrize("slope", [0.03, -0.02, 0.05])
def test_known_slope_is_recovered(slope):
    tr = run(synthetic(slope))
    assert tr["slope_per_decade"] == pytest.approx(slope * 10, abs=0.05)
    lo, hi = tr["ci95"]
    assert lo <= slope * 10 <= hi
    assert tr["direction"] == ("increasing" if slope > 0 else "decreasing")
    assert tr["robustness"]["methods_agree"]


def test_no_trend_is_not_invented():
    tr = run(synthetic(0.0, noise=0.5, seed=3))
    assert tr["direction"] == "no_trend"
    assert tr["ci95"][0] <= 0 <= tr["ci95"][1]


def test_seasons_alone_do_not_make_a_trend():
    df = synthetic(0.0, noise=0.01, seed=1)
    tr = run(df)
    assert abs(tr["slope_per_decade"]) < 0.01


def test_fill_values_become_missing_and_lower_completeness():
    df = synthetic(0.02)
    df.loc[:59, "value"] = -999.0           # first 5 years lost
    cleaned = clean(df, "T2M")
    assert cleaned["value"].isna().sum() == 60
    assert completeness(cleaned) == pytest.approx(1 - 60 / 540, abs=1e-3)
    assert len(annual_values(cleaned, "T2M")) == 40


def test_rain_is_converted_to_mm_per_month_and_summed():
    dates = pd.date_range("1981-01-01", "1981-12-01", freq="MS")
    df = pd.DataFrame({"date": dates, "value": 1.0})       # 1 mm/day all year
    annual = annual_values(clean(df, "PRECTOTCORR"), "PRECTOTCORR")
    assert annual["value"].iloc[0] == pytest.approx(365)


def test_anomalies_average_zero_per_month():
    anom = monthly_anomalies(synthetic(0.02))
    means = anom.groupby(anom["date"].dt.month)["anomaly"].mean()
    assert np.allclose(means, 0, atol=1e-9)


def test_verdict_labels():
    var = config.VARIABLES["T2M"]
    robust = run(synthetic(0.04))
    assert make_verdict(var, robust, 1.0, 45, 1981, "nasa")["label"] == "significant_robust"
    flat = run(synthetic(0.0, noise=0.5, seed=3))
    assert make_verdict(var, flat, 1.0, 45, 1981, "nasa")["label"] == "no_clear_trend"
    assert make_verdict(var, None, 0.5, 20, 1981, "nasa")["label"] == "insufficient_data"
