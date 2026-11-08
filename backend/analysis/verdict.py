"""Numbers -> one of four labels, plain sentences and honest caveats.

The four labels (rules decided on paper, checked in this order):
  insufficient_data   completeness < 80 % or fewer than 30 full years
  no_clear_trend      Seasonal Kendall p >= alpha
  significant_fragile Seasonal Kendall p < alpha, but Hamed-Rao or OLS disagrees
  significant_robust  Seasonal Kendall, Hamed-Rao and OLS all p < alpha, same sign
"""
import config


def _fmt(x: float) -> str:
    ax = abs(x)
    if ax >= 10:
        return f"{ax:.0f}"
    if ax >= 1:
        return f"{ax:.1f}"
    return f"{ax:.2f}"


def make_verdict(var: dict, trend: dict | None, completeness: float, n_years: int,
                 start_year: int, origin: str) -> dict:
    unit = var["unit"]
    per_decade_unit = unit.replace("/year", "") if unit.endswith("/year") else unit
    caveats = [var["confidence_note"], "One grid cell of about 55 x 60 km, not a single town"]
    if origin == "snapshot":
        caveats.append("NASA POWER did not answer; this uses a saved copy")

    if trend is None or completeness < config.MIN_COMPLETENESS or n_years < config.MIN_YEARS:
        return {
            "label": "insufficient_data",
            "headline": "Not enough data to judge.",
            "explanation": f"Only {n_years} complete years ({completeness:.0%} of months) are available; "
                           f"MIZAN needs at least {config.MIN_YEARS} years.",
            "caveats": caveats,
        }

    name = var["name"]
    slope = trend["slope_per_decade"]
    lo, hi = trend["ci95"]
    up, down = ("more", "less") if var["annual"] == "sum" else ("higher", "lower")
    more_less = up if slope > 0 else down

    if trend["direction"] == "no_trend":
        return {
            "label": "no_clear_trend",
            "headline": f"No clear change in {name.lower()} here.",
            "explanation": f"Since {start_year} the data do not show a trend that stands out from normal "
                           f"year-to-year variation (p = {trend['p_value']:.2f}).",
            "caveats": caveats,
        }

    word = var["words"][trend["direction"]]
    headline = f"{name} is {word} here."
    size = f"About {_fmt(slope)} {per_decade_unit} {more_less} per decade since {start_year}"
    interval = f" (95% range: {lo:+.2g} to {hi:+.2g} per decade)"

    if trend["robustness"]["methods_agree"]:
        return {
            "label": "significant_robust",
            "headline": headline,
            "explanation": size + interval + "; all three methods agree.",
            "caveats": caveats,
        }

    caveats.append("The trend weakens when year-to-year memory in the data is accounted for")
    return {
        "label": "significant_fragile",
        "headline": f"{name} is probably {word} here.",
        "explanation": size + interval + "; but not every method agrees, so treat it as a hint.",
        "caveats": caveats,
    }
