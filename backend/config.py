"""Everything MIZAN needs to know that is not code: questions, variables, presets, period."""

START_YEAR = 1981
END_YEAR = 2025
ALPHA = 0.05                 # significance level for every test
MIN_COMPLETENESS = 0.8       # share of months that must be present
MIN_YEARS = 30               # shortest series we accept for a trend

POWER_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
POWER_COMMUNITY = "AG"
POWER_TIMEOUT = 30           # seconds
FILL_VALUE = -999.0

# MERRA-2 native grid used by POWER: 0.5 deg latitude x 0.625 deg longitude
GRID_DLAT = 0.5
GRID_DLON = 0.625

VARIABLES = {
    "T2M": {
        "code": "T2M",
        "question": "Is it getting hotter?",
        "name": "Average temperature",
        "unit": "°C",
        "power_unit": "C",
        "annual": "mean",
        "definition": "Air temperature 2 metres above the ground, averaged over day and night.",
        "confidence_note": "Reanalysis temperature: good confidence for trends",
        "confidence": "high",
        "words": {"increasing": "rising", "decreasing": "falling"},
    },
    "T2M_MAX": {
        "code": "T2M_MAX",
        "question": "Are the hottest hours getting hotter?",
        "name": "Daily maximum temperature",
        "unit": "°C",
        "power_unit": "C",
        "annual": "mean",
        "definition": "The highest temperature of each day, 2 metres above the ground, averaged over the month.",
        "confidence_note": "Reanalysis temperature: good confidence for trends",
        "confidence": "high",
        "words": {"increasing": "rising", "decreasing": "falling"},
    },
    "PRECTOTCORR": {
        "code": "PRECTOTCORR",
        "question": "Is it raining less?",
        "name": "Rainfall",
        "unit": "mm/year",
        "power_unit": "mm/day",
        "annual": "sum",
        "definition": "Total rain and snow reaching the ground, bias-corrected with gauge data.",
        "confidence_note": "Reanalysis rainfall: lower confidence for trends",
        "confidence": "low",
        "words": {"increasing": "increasing", "decreasing": "decreasing"},
    },
    "WS10M": {
        "code": "WS10M",
        "question": "Is it getting windier?",
        "name": "Wind speed",
        "unit": "m/s",
        "power_unit": "m/s",
        "annual": "mean",
        "definition": "Average wind speed 10 metres above the ground.",
        "confidence_note": "Reanalysis wind: medium confidence for trends",
        "confidence": "medium",
        "words": {"increasing": "increasing", "decreasing": "decreasing"},
    },
}

PRESETS = [
    {"id": "essaouira", "name": "Essaouira coast", "lat": 31.51, "lon": -9.77},
    {"id": "marrakech", "name": "Marrakech", "lat": 31.63, "lon": -7.99},
    {"id": "agadir", "name": "Agadir", "lat": 30.42, "lon": -9.60},
    {"id": "ouarzazate", "name": "Ouarzazate", "lat": 30.92, "lon": -6.91},
    {"id": "ifrane", "name": "Ifrane (Middle Atlas)", "lat": 33.53, "lon": -5.11},
    {"id": "casablanca", "name": "Casablanca", "lat": 33.57, "lon": -7.59},
]
