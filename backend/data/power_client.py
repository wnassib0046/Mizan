"""Talks to NASA POWER. Cache first, then the API, then a saved snapshot."""
import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

import config

HERE = Path(__file__).parent
CACHE_DIR = HERE / "cache"
SNAPSHOT_DIR = HERE / "snapshots"


class NasaUnavailable(Exception):
    """POWER did not answer and no saved copy exists."""


def grid_cell(lat: float, lon: float) -> dict:
    """Centre of the MERRA-2 cell that contains the point."""
    return {
        "lat": round(round(lat / config.GRID_DLAT) * config.GRID_DLAT, 3),
        "lon": round(round(lon / config.GRID_DLON) * config.GRID_DLON, 3),
    }


def _key(lat, lon, parameter, start, end) -> str:
    return f"{parameter}_{lat:.2f}_{lon:.2f}_{start}_{end}".replace("-", "m")


def build_url(lat, lon, parameter, start, end) -> tuple[str, dict]:
    params = {
        "parameters": parameter,
        "community": config.POWER_COMMUNITY,
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "start": start,
        "end": end,
        "format": "JSON",
    }
    return config.POWER_URL, params


def _call_power(lat, lon, parameter, start, end, retries=2) -> dict:
    url, params = build_url(lat, lon, parameter, start, end)
    last_error = None
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=config.POWER_TIMEOUT)
            if r.status_code == 200:
                return r.json()
            last_error = f"HTTP {r.status_code}: {r.text[:200]}"
            if 400 <= r.status_code < 500:
                break           # our request is wrong; retrying will not help
        except requests.RequestException as e:
            last_error = str(e)
        time.sleep(1.5 * (attempt + 1))
    raise NasaUnavailable(last_error)


def to_dataframe(payload: dict, parameter: str) -> pd.DataFrame:
    """POWER JSON -> DataFrame with columns date (month start) and value.

    POWER keys look like '198101'..'198112' plus '198113' for the annual value,
    which we drop: annual values are computed by us, consistently.
    """
    values = payload["properties"]["parameter"][parameter]
    rows = []
    for key, v in values.items():
        month = int(key[4:])
        if 1 <= month <= 12:
            rows.append({"date": pd.Timestamp(int(key[:4]), month, 1), "value": v})
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


def fetch_monthly(lat: float, lon: float, parameter: str,
                  start: int = config.START_YEAR, end: int = config.END_YEAR):
    """Returns (DataFrame, info). info says where the data came from."""
    CACHE_DIR.mkdir(exist_ok=True)
    key = _key(lat, lon, parameter, start, end)
    cache_file = CACHE_DIR / f"{key}.json"

    if cache_file.exists():
        payload = json.loads(cache_file.read_text())
        return to_dataframe(payload, parameter), {"origin": "cache", "retrieved": payload.get("_retrieved")}

    try:
        payload = _call_power(lat, lon, parameter, start, end)
        payload["_retrieved"] = date.today().isoformat()
        cache_file.write_text(json.dumps(payload))
        return to_dataframe(payload, parameter), {"origin": "nasa", "retrieved": payload["_retrieved"]}
    except NasaUnavailable:
        snap = _find_snapshot(lat, lon, parameter)
        if snap is None:
            raise
        payload = json.loads(snap.read_text())
        return to_dataframe(payload, parameter), {"origin": "snapshot", "retrieved": payload.get("_retrieved")}


def _find_snapshot(lat, lon, parameter):
    """A snapshot for the same parameter within ~0.3 deg of the point."""
    if not SNAPSHOT_DIR.exists():
        return None
    best, best_d = None, 0.3
    for f in SNAPSHOT_DIR.glob(f"{parameter}_*.json"):
        try:
            rest = f.stem[len(parameter) + 1:]          # "31.51_m9.77_1981_2025"
            slat, slon, *_ = rest.replace("m", "-").split("_")
            d =max(abs(float(slat) - lat), abs(float(slon) - lon))
        except ValueError:
            continue
        if d <= best_d:
            best, best_d = f, d
    return best
