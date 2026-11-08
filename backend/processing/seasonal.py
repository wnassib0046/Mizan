"""Monthly climatology, anomalies and annual values."""
import pandas as pd

import config


def climatology(df: pd.DataFrame) -> pd.Series:
    """Average value for each calendar month (index 1..12)."""
    return df.groupby(df["date"].dt.month)["value"].mean()


def monthly_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Each month minus the average of that calendar month: removes the seasons."""
    clim = climatology(df)
    out = df.copy()
    out["anomaly"] = out["value"] - out["date"].dt.month.map(clim)
    return out


def annual_values(df: pd.DataFrame, parameter: str) -> pd.DataFrame:
    """One value per year: sum for rainfall, mean otherwise. Years with a missing month are dropped."""
    how = config.VARIABLES[parameter]["annual"]
    g = df.groupby(df["date"].dt.year)["value"]
    counts = g.count()
    agg = g.sum() if how == "sum" else g.mean()
    agg = agg[counts == 12]
    return pd.DataFrame({"year": agg.index.astype(int), "value": agg.values})
