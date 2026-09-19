# Q-TRAFFIC — Shree Module v2

## Shree's responsibility
- Traffic state processing
- Traffic prediction
- Traffic shock propagation
- Demand forecasting
- Location/scenario-aware prediction output
- Prediction confidence
- Dashboard-ready traffic data

Shree does **not** control signals or implement QUBO/QAOA.

## New dashboard contract
The module produces:
- `location`
- `scenario`
- per-junction density, queue, speed, capacity
- 1/3/5 minute predictions
- model confidence for each horizon
- shock source, propagation order, and intensity
- demand forecast
- explicit simulated/location-inspired metadata

Locations and scenarios are simulated/location-inspired presets, not live traffic claims.

## Current preset
`Coimbatore + TEXTILE_FESTIVAL`

Other presets in `config/scenarios.py`:
- `Coimbatore + SCHOOL_PEAK`
- `Coimbatore + NORMAL`

Add more locations later by configuration; do not create separate models per city.

## Run
```powershell
..\venv\Scripts\python.exe main.py
```

Tests:
```powershell
..\venv\Scripts\python.exe -m pytest
```
