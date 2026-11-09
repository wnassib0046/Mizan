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

## Space Apps challenge

_TODO: name the 2026 NASA Space Apps challenge MIZAN answers, link to it, and say in two sentences how MIZAN addresses it._

## Data and citation

These data were obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program. Source: MERRA-2 reanalysis, native grid 0.5° × 0.625° (about 55 × 60 km), monthly, 1981–2025.
`backend/data/snapshots/` holds saved answers for the preset places so the demo still works if POWER is down.

- NASA POWER: https://power.larc.nasa.gov (monthly point API, `community=AG`)
- Gelaro, R., et al. (2017). The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2). *Journal of Climate*, 30(14), 5419–5454.
- Map data © OpenStreetMap contributors, available under the Open Database License (ODbL): https://www.openstreetmap.org/copyright. Map tiles from tile.openstreetmap.org, used under the OSM tile usage policy.

## Methods references

- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259.
- Kendall, M. G. (1975). *Rank Correlation Methods*. Griffin, London.
- Hirsch, R. M., Slack, J. R., & Smith, R. A. (1982). Techniques of trend analysis for monthly water quality data. *Water Resources Research*, 18(1), 107–121. (Seasonal Kendall test)
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. *Journal of the American Statistical Association*, 63(324), 1379–1389.
- Hamed, K. H., & Rao, A. R. (1998). A modified Mann-Kendall trend test for autocorrelated data. *Journal of Hydrology*, 204(1–4), 182–196.
- Hussain, M., & Mahmud, I. (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests. *Journal of Open Source Software*, 4(39), 1556.

## Third-party software and licenses

All third-party software is open source (OSI-approved licenses). Versions are those MIZAN was tested with.

| Software | Used for | Version | License |
|---|---|---|---|
| [FastAPI](https://github.com/fastapi/fastapi) | Web API | 0.162.2 | MIT |
| [Uvicorn](https://github.com/encode/uvicorn) | Web server | 0.50.2 | BSD-3-Clause |
| [Requests](https://github.com/psf/requests) | Calls to NASA POWER | 2.34.2 | Apache-2.0 |
| [pandas](https://github.com/pandas-dev/pandas) | Data tables | 3.0.1 | BSD-3-Clause |
| [NumPy](https://github.com/numpy/numpy) | Numerical arrays | 2.2.6 | BSD-3-Clause |
| [SciPy](https://github.com/scipy/scipy) | Sen's slope interval, OLS | 1.17.1 | BSD-3-Clause |
| [pyMannKendall](https://github.com/mmhs013/pyMannKendall) | Seasonal and Hamed-Rao Mann-Kendall tests | 1.4.3 | MIT |
| [pytest](https://github.com/pytest-dev/pytest) | Tests | 9.2.0 | MIT |
| [Leaflet](https://github.com/Leaflet/Leaflet) | Interactive map | 1.9.4 | BSD-2-Clause |
| [Plotly.js](https://github.com/plotly/plotly.js) | Charts | 2.35.2 | MIT |

## License

MIZAN's own code is released under the Apache License 2.0; see [LICENSE](LICENSE).

## AI-use note

Parts of this code were written with the help of Claude (Anthropic), working from the team's technical blueprint. The team reviewed, tested, and is responsible for all of it.
