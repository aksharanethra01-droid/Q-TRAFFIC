# Quantum-Enhanced Adaptive Urban Traffic Optimization

A four-intersection adaptive traffic-control research/hackathon project for **J1 → J2 → J3 → J4**. The system connects traffic-state monitoring, lightweight prediction, graph-based traffic-shock propagation, a mathematically explicit 12-variable QUBO, actual QAOA execution through Qiskit Aer when available, signal-plan decoding, SUMO/TraCI integration, emergency clearance-aware coordination, bilingual alerts, transparent simulation metrics, and a Streamlit dashboard.

## Architecture

Observe → Predict → Propagate → QUBO → QAOA → Decode → SUMO/TraCI → Observe again.

Emergency path: detect ambulance → calculate route → inspect downstream queue/occupancy → activate a coordinated corridor only when clearance is available → track passage → release corridor → return to normal optimization.

## QUBO

There are exactly 12 binary variables:

- J1_P1, J1_P2, J1_P3
- J2_P1, J2_P2, J2_P3
- J3_P1, J3_P2, J3_P3
- J4_P1, J4_P2, J4_P3

Each junction uses the constraint `(x1 + x2 + x3 - 1)^2`, with configurable penalty. The objective includes waiting, queue, throughput, congestion, spillback, emergency delay, fuel, CO2, and signal-change penalty. The previous rolling-horizon plan is included to penalize unnecessary changes.

## QAOA

`quantum/qaoa_optimizer.py` converts the QUBO into an Ising representation, builds a p-layer QAOA circuit with Hadamard initialization, cost `RZ/RZZ` layers, `RX` mixer layers, parameter search, Aer execution, measurement, valid-solution selection, and decoding.

**QAOA is approximate. QAOA is not automatically better than classical optimization. The benchmark is empirical.** If Qiskit/Aer is unavailable or execution fails, the program reports `FALLBACK` and uses the exact classical 3^4 = 81-combination QUBO search. It never labels that result QAOA.

## Classical baseline

The project includes:
1. fixed-time controller,
2. rule-based controller,
3. exact classical QUBO search over all 81 valid combinations,
4. measured QAOA when Aer is available.

No improvement percentage is fabricated. The dashboard and outputs expose measured values/status.

## SUMO + TraCI

The `sumo/` directory contains nodes, edges, a network file, route demand, traffic-light programs, and a SUMO configuration. The demand includes normal vehicles and `AMB01`. `run_sumo.py` uses actual SUMO and TraCI. If SUMO is absent it reports: `SUMO is not installed/configured.` It does not silently replace SUMO with a Python simulation.

To regenerate the network from source XML, run `python sumo/build_network.py` after installing SUMO and making `netconvert` available.

## Rolling horizon and warm start

The demo re-optimizes at each scenario event. The previous plan is passed to the next QUBO and unnecessary signal changes receive a penalty.

## Emergency Green Corridor

`emergency/green_corridor.py` does not simply set every signal green. It checks downstream queue and occupancy against clearance thresholds before activating coordinated emergency phases. If the corridor is blocked, the decision is `HOLD`.

## Alerts

Automatic English/Tamil alerts are generated for obstruction, accident, and ambulance events. Police do not need to type or speak commands. Optional Edge-TTS can create English and Tamil audio. If unavailable, the status is `TTS UNAVAILABLE`.

## Metrics

Fuel and CO2 are explicitly labeled **SIMULATION ESTIMATE**. They are transparent proportional estimates, not measured fuel consumption or emissions.

Outputs:
- `outputs/metrics.csv`
- `outputs/optimization_history.csv`
- `outputs/alerts.json`
- `outputs/qaoa_results.json`
- `outputs/scenario_results.json`

## Scenario timeline

- t=0 NORMAL
- t=60 SCHOOL_PEAK
- t=120 TEXTILE_FESTIVAL / CROWD_SURGE
- t=180 VEHICLE_OBSTRUCTION at J2, TN38AB1234, Sedan
- t=240 ACCIDENT at J3
- t=300 AMBULANCE AMB01, route J1 → J2 → J3 → J4
- recovery follows

Vehicle numbers/models in the demo are **simulated metadata**. Location presets are simulations, not live traffic.

## Location presets

Coimbatore, Chennai, Madurai, and Salem are simulation presets with traffic/peak/event/capacity multipliers. The project does not claim live traffic.

## Windows setup

Install Python 3.11+ and optionally SUMO.

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run_demo.py
python -m pytest -q
streamlit run dashboard/app.py
python run_sumo.py
```

If SUMO is installed, set `SUMO_HOME` to the SUMO installation directory and ensure its `bin` directory is available to Python/Windows PATH.

## Testing

```powershell
python -m compileall .
python -m pytest -q
python run_demo.py
```

## Limitations

- QAOA is a small-scale experimental optimizer; it is not guaranteed to outperform exact classical optimization.
- The QAOA parameter search is deliberately compact for a hackathon demo.
- The included network is a small corridor, not a city-scale calibrated model.
- Traffic prediction uses weighted moving average + trend extrapolation, not a neural network.
- Fuel and CO2 are simulation estimates.
- Location presets and event metadata are simulated.
- Real deployments require calibrated traffic data, signal engineering validation, safety certification, and operational integration.

## Future work

- Calibrate the prediction model against historical detector data.
- Expand the SUMO network and include multi-modal demand.
- Evaluate QAOA across repeated seeds and parameter optimizers.
- Add live detector/ATCS integration only after appropriate validation.
- Add richer emergency priority constraints and safety-certified signal plans.
