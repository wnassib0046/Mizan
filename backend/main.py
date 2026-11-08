"""MIZAN backend: four routes, one error shape, and it serves the frontend.

Run from this folder:  python -m uvicorn main:app --reload
Then open:             http://127.0.0.1:8000        (the app)
                       http://127.0.0.1:8000/docs   (try the API)
"""
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from analysis.trend import analyze_trend
from analysis.verdict import make_verdict
from data.power_client import NasaUnavailable, fetch_monthly, grid_cell
from processing.clean import clean, completeness
from processing.seasonal import annual_values, monthly_anomalies

app = FastAPI(title="MIZAN API", version="1.0")

# Development only: lets Live Server (port 5500) call us on port 8000.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": code, "message": message})


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/variables")
def variables():
    keys = ("code", "question", "name", "unit", "definition", "confidence_note", "confidence")
    return [{k: v[k] for k in keys} for v in config.VARIABLES.values()]


@app.get("/api/presets")
def presets():
    return config.PRESETS


@app.get("/api/analyze")
def analyze(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    variable: str = Query("T2M"),
    name: str | None = Query(None, description="Optional place name to echo back"),
):
    variable = variable.upper()
    if variable not in config.VARIABLES:
        return error(400, "unknown_variable", f"'{variable}' is not one of {list(config.VARIABLES)}.")
    var = config.VARIABLES[variable]

    try:
        raw, info = fetch_monthly(lat, lon, variable)
    except NasaUnavailable:
        return error(503, "nasa_unavailable", "NASA POWER did not answer and no saved copy exists for this place. Try again in a minute.")

    df = clean(raw, variable)
    comp = completeness(df)
    anom = monthly_anomalies(df)
    annual = annual_values(df, variable)

    trend = None
    if comp >= config.MIN_COMPLETENESS and len(annual) >= config.MIN_YEARS:
        trend = analyze_trend(df, annual)

    verdict = make_verdict(var, trend, comp, len(annual), config.START_YEAR, info["origin"])

    return {
        "location": {
            "name": name or f"{lat:.2f}, {lon:.2f}",
            "requested": {"lat": lat, "lon": lon},
            "grid_cell": grid_cell(lat, lon),
        },
        "variable": {k: var[k] for k in ("code", "question", "name", "unit", "confidence_note")},
        "period": {
            "start": f"{config.START_YEAR}-01",
            "end": f"{config.END_YEAR}-12",
            "completeness": comp,
        },
        "series": {
            "annual": [{"year": int(r.year), "value": round(float(r.value), 3)} for r in annual.itertuples()],
            "monthly_anomaly": [
                {"date": r.date.strftime("%Y-%m"), "value": None if r.anomaly != r.anomaly else round(float(r.anomaly), 3)}
                for r in anom.itertuples()
            ],
        },
        "trend": trend,
        "verdict": verdict,
        "source": f"NASA POWER (MERRA-2), monthly, retrieved {info.get('retrieved') or 'unknown'}"
                  + (" (saved copy)" if info["origin"] == "snapshot" else ""),
    }


# Serve the frontend from the same address, so no CORS is needed online.
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
