# Q-TRAFFIC — San Independent Module

This is **San's work only**. It does not implement SUMO, QUBO/QAOA, prediction, or the dashboard.

## Workflow
Emergency vehicle → congestion-aware routing → best route → Green Corridor → clearance → junction states → recovery → fuel/CO2 → dashboard-ready JSON.

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run
```powershell
python -m san.main
```

## Test
```powershell
python -m unittest san\test_san.py
```

Expected: `Ran 8 tests` and `OK`.

## Files
- emergency.py — ambulance model
- routing.py — congestion-aware routing and closed-road handling
- corridor.py — Green Corridor, clearance and junction states
- recovery.py — recovery after emergency
- emissions.py — prototype fuel/CO2 estimate
- dashboard_output.py — structured output for Aksh later
- main.py — standalone demo
- test_san.py — tests
- data/traffic_state.json — example traffic-state input

Fuel/CO2 are simulation-based prototype estimates, not measured real-world values.
