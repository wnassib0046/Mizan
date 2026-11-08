"""-999 -> NaN, unit conversion, completeness check."""
import numpy as np
import pandas as pd

import config


def clean(df: pd.DataFrame, parameter: str) -> pd.DataFrame:
    out = df.copy()
    out["value"] = out["value"].astype(float)
    out.loc[out["value"] <= config.FILL_VALUE + 1e-6, "value"] = np.nan

    # Rainfall arrives as mm/day averaged over the month; we want mm/month,
    # so the annual sum is a real yearly total in mm/year.
    if config.VARIABLES[parameter]["power_unit"] == "mm/day":
        out["value"] = out["value"] * out["date"].dt.days_in_month
    return out


def completeness(df: pd.DataFrame, start: int = config.START_YEAR, end: int = config.END_YEAR) -> float:
    expected = (end - start + 1) * 12
    return round(float(df["value"].notna().sum()) / expected, 3)
