# MIZAN

**Is the climate where you live really changing?** Click a place, pick a question, and MIZAN weighs 45 years of NASA data (1981–2025) to give an honest verdict: a clear change, a possible change, no clear change, or not enough data.

## Run it

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000 for the app and http://127.0.0.1:8000/docs to try the API.

Frontend-only work: open `frontend/index.html` with VS Code Live Server (port 5500) while the backend runs, or add `?mock=1` to the address to use `frontend/mock/analyze.json` with no backend.

Tests: `cd backend && python -m pytest -q`

## How it works

```
browser (Leaflet map, Plotly chart)  ->  GET /api/analyze  ->  FastAPI
   -> power_client (cache -> NASA POWER -> snapshot)  -> clean (-999 -> NaN, mm/day -> mm/month)
   -> seasonal (anomalies, annual values) -> trend (Seasonal Kendall, Sen, Hamed-Rao, OLS)
   -> verdict (label, sentences, caveats)  ->  JSON  ->  chart + verdict card
```

| Route | Answer |
|---|---|
| `GET /api/health` | `{"status": "ok"}` |
| `GET /api/variables` | questions, units, definitions, confidence notes |
| `GET /api/presets` | preset places |
| `GET /api/analyze?lat=&lon=&variable=` | one full analysis |

Errors always look like `{"error": "<code>", "message": "<plain sentence>"}`.

### Verdict rules (alpha = 0.05)

1. **insufficient_data**: under 80 % of months, or under 30 complete years.
2. **no_clear_trend**: Seasonal Mann-Kendall p ≥ 0.05.
3. **significant_fragile**: Seasonal Mann-Kendall p < 0.05, but Hamed-Rao (autocorrelation-corrected) or OLS disagrees.
4. **significant_robust**: all three p < 0.05 with the same sign.

The size of the change is Sen's slope on annual values, with a 95 % interval.

## Data and citation

These data were obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program. Source: MERRA-2 reanalysis, native grid 0.5° × 0.625° (about 55 × 60 km), monthly.
`backend/data/snapshots/` holds saved answers for the preset places so the demo still works if POWER is down.

## AI-use note

Parts of this code were written with the help of Claude (Anthropic), working from the team's technical blueprint. The team reviewed, tested, and is responsible for all of it.
