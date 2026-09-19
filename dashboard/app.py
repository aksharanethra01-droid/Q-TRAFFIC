import requests
import streamlit as st
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Q-TRAFFIC | Traffic Command Center",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 20px;
            color: #666;
            margin-bottom: 25px;
        }

        .status-card {
            padding: 18px;
            border-radius: 12px;
            border: 1px solid #ddd;
            text-align: center;
            font-weight: 600;
            min-height: 70px;
        }

        .section-title {
            font-size: 30px;
            font-weight: 700;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        .success-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #e8f7ee;
            border: 1px solid #b7e4c7;
            color: #137333;
            font-weight: 600;
        }

        .warning-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #fff7e6;
            border: 1px solid #f4d58d;
            color: #8a5a00;
            font-weight: 600;
        }

        .danger-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #fdecec;
            border: 1px solid #f2b8b5;
            color: #a61b1b;
            font-weight: 600;
        }

        .route-box {
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #ddd;
            background-color: #fafafa;
            font-size: 24px;
            font-weight: 700;
            text-align: center;
        }

        div[data-testid="stMetric"] {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "health" not in st.session_state:
    st.session_state.health = None


# ============================================================
# API HELPERS
# ============================================================

def api_get(endpoint):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def api_post(endpoint, payload):
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        st.error(f"API request failed: {exc}")
        return None


# ============================================================
# HEALTH CHECK
# ============================================================

health = api_get("/health")
st.session_state.health = health

api_connected = health is not None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## LOCATION")

    locations_response = api_get("/locations")

    locations = [
        "Coimbatore",
        "Chennai",
        "Madurai",
        "Salem",
    ]

    if isinstance(locations_response, list):
        locations = locations_response

    elif isinstance(locations_response, dict):
        if "locations" in locations_response:
            locations = locations_response["locations"]

    location = st.selectbox(
        "Select Location",
        locations
    )

    st.markdown("## TRAFFIC SCENARIO")

    scenarios_response = api_get("/scenarios")

    scenarios = [
        "Normal Traffic",
        "School Peak",
        "Textile Festival",
        "Accident",
        "Vehicle Obstruction",
        "Ambulance Emergency",
    ]

    if isinstance(scenarios_response, list):
        scenarios = scenarios_response

    elif isinstance(scenarios_response, dict):
        if "scenarios" in scenarios_response:
            scenarios = scenarios_response["scenarios"]

    scenario = st.selectbox(
        "Select Scenario",
        scenarios
    )

    st.divider()

    if api_connected:
        st.success("FASTAPI CONNECTED")
        st.caption(
            "Dashboard is connected to the Q-TRAFFIC API."
        )
    else:
        st.error("FASTAPI OFFLINE")
        st.caption(
            "Start FastAPI using: uvicorn api.main:app --reload"
        )

    if st.button(
        "RUN SCENARIO ANALYSIS",
        type="primary",
        use_container_width=True,
    ):

        if not api_connected:
            st.error("FastAPI is not running.")
        else:

            with st.spinner(
                "Running Shree prediction, San emergency routing and Nila QAOA..."
            ):

                result = api_post(
                    "/scenario/run",
                    {
                        "location": location,
                        "scenario": scenario,
                    },
                )

            if result:
                st.session_state.result = result
                st.success("Scenario analysis completed.")

    if st.button(
        "RESET",
        use_container_width=True,
    ):
        st.session_state.result = None
        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🚦 Q-TRAFFIC COMMAND CENTER</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Hybrid Quantum-Classical Traffic Intelligence</div>',
    unsafe_allow_html=True,
)

st.caption(
    "FastAPI-connected multi-intersection traffic optimization, "
    "congestion intelligence, emergency routing and quantum signal optimization."
)


# ============================================================
# SYSTEM STATUS
# ============================================================

status1, status2, status3, status4 = st.columns(4)

with status1:
    if api_connected:
        st.success("API CONNECTED")
    else:
        st.error("API OFFLINE")

with status2:
    st.info("QUBO / QAOA")

with status3:
    st.info("4-INTERSECTION PROTOTYPE")

with status4:
    st.info("SIMULATION MODE")


result = st.session_state.result


if result is None:

    st.info(
        "Select a location and scenario from the sidebar, "
        "then click RUN SCENARIO ANALYSIS."
    )

    st.stop()


st.success("Scenario analysis completed successfully.")


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_dict(value):
    return value if isinstance(value, dict) else {}


def safe_list(value):
    return value if isinstance(value, list) else []


def number(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


def display_number(value):
    value = number(value)

    if value.is_integer():
        return int(value)

    return round(value, 2)


# ============================================================
# EXTRACT RESULTS
# ============================================================

junctions = safe_dict(result.get("junctions"))
predictions = safe_dict(result.get("predictions"))
emergency = safe_dict(result.get("emergency"))
qaoa = safe_dict(result.get("qaoa"))
controllers = safe_dict(result.get("controllers"))
metrics = safe_dict(result.get("metrics"))
audit = safe_dict(result.get("audit"))

event = safe_dict(result.get("event"))

location_value = result.get("location", location)
scenario_value = result.get("scenario", scenario)


# ============================================================
# SCENARIO
# ============================================================

st.markdown(
    '<div class="section-title">🎯 Scenario</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Location",
        location_value
    )

with c2:
    st.metric(
        "Scenario",
        scenario_value
    )

with c3:
    st.metric(
        "Active Event",
        event.get("type", "NONE")
    )


# ============================================================
# NETWORK PERFORMANCE
# ============================================================

st.markdown(
    '<div class="section-title">📊 Network Performance</div>',
    unsafe_allow_html=True,
)


total_vehicles = 0
total_queue = 0

for junction in junctions.values():

    if isinstance(junction, dict):

        total_vehicles += int(
            number(junction.get("vehicles", 0))
        )

        total_queue += int(
            number(junction.get("queue", 0))
        )


hybrid_metrics = safe_dict(
    controllers.get("Quantum-Hybrid Prototype")
)

average_waiting = hybrid_metrics.get(
    "average_waiting_time",
    0
)

throughput = hybrid_metrics.get(
    "throughput",
    0
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Vehicles",
        display_number(total_vehicles)
    )

with m2:
    st.metric(
        "Total Queue",
        display_number(total_queue)
    )

with m3:
    st.metric(
        "Average Waiting",
        f"{display_number(average_waiting)} sec"
    )

with m4:
    st.metric(
        "Throughput",
        display_number(throughput)
    )


# ============================================================
# ROAD NETWORK
# ============================================================

st.markdown(
    '<div class="section-title">🛣️ Road Network</div>',
    unsafe_allow_html=True,
)

road_rows = []

for junction_id, data in junctions.items():

    data = safe_dict(data)

    road_rows.append(
        {
            "Junction": junction_id,
            "Vehicles": display_number(
                data.get("vehicles", 0)
            ),
            "Queue": display_number(
                data.get("queue", 0)
            ),
            "Speed": display_number(
                data.get("speed", 0)
            ),
            "Capacity": display_number(
                data.get("capacity", 0)
            ),
            "Signal": data.get(
                "signal",
                "N/A"
            ),
        }
    )


if road_rows:

    st.dataframe(
        pd.DataFrame(road_rows),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SHREE TRAFFIC PREDICTION
# ============================================================

st.markdown(
    '<div class="section-title">🧠 Congestion Intelligence</div>',
    unsafe_allow_html=True,
)

prediction_rows = []

for junction_id, prediction in predictions.items():

    prediction = safe_dict(prediction)

    current = safe_dict(
        junctions.get(junction_id)
    )

    prediction_rows.append(
        {
            "Junction": junction_id,
            "Current Vehicles": display_number(
                current.get("vehicles", 0)
            ),
            "1 min": display_number(
                prediction.get("1min", 0)
            ),
            "3 min": display_number(
                prediction.get("3min", 0)
            ),
            "5 min": display_number(
                prediction.get("5min", 0)
            ),
            "Current Queue": display_number(
                current.get("queue", 0)
            ),
        }
    )


if prediction_rows:

    st.dataframe(
        pd.DataFrame(prediction_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Prediction source: Shree traffic prediction module"
    )


# ============================================================
# EMERGENCY GREEN CORRIDOR
# ============================================================

st.markdown(
    '<div class="section-title">🚑 Emergency Green Corridor</div>',
    unsafe_allow_html=True,
)

vehicle = emergency.get(
    "vehicle",
    "AMB01"
)

route = emergency.get(
    "selected_route",
    emergency.get(
        "route",
        []
    )
)

if not route:
    route = []

route_text = " → ".join(
    str(x) for x in route
)

if not route_text:
    route_text = "Route unavailable"


e1, e2 = st.columns(2)

with e1:
    st.metric(
        "Emergency Vehicle",
        vehicle
    )

with e2:
    st.metric(
        "Priority",
        emergency.get(
            "priority",
            "HIGH"
        )
    )


st.markdown(
    f"""
    <div class="route-box">
        🚑 {route_text}
    </div>
    """,
    unsafe_allow_html=True,
)


corridor_status = emergency.get(
    "corridor_status",
    emergency.get(
        "status",
        "READY"
    )
)

if str(corridor_status).upper() in [
    "READY",
    "ACTIVE",
    "GREEN",
]:

    st.success(
        f"GREEN CORRIDOR: {corridor_status}"
    )

else:

    st.warning(
        f"GREEN CORRIDOR: {corridor_status}"
    )


# ============================================================
# ROUTE CLEARANCE
# ============================================================

clearance = safe_dict(
    emergency.get("clearance")
)

if clearance:

    st.subheader("Route Clearance")

    clear_value = clearance.get(
        "clear",
        False
    )

    action = clearance.get(
        "action",
        "UNKNOWN"
    )

    if clear_value:

        st.success(
            f"✅ ROUTE CLEAR — {action}"
        )

    else:

        st.warning(
            f"⚠️ ROUTE STATUS — {action}"
        )

    clearance_junctions = safe_list(
        clearance.get("junctions")
    )

    clearance_rows = []

    for item in clearance_junctions:

        item = safe_dict(item)

        clearance_rows.append(
            {
                "Junction": item.get(
                    "junction",
                    "N/A"
                ),
                "Current Queue": display_number(
                    item.get(
                        "queue",
                        0
                    )
                ),
                "Predicted": display_number(
                    item.get(
                        "predicted",
                        0
                    )
                ),
                "Capacity": display_number(
                    item.get(
                        "capacity",
                        0
                    )
                ),
                "Capacity Status":
                    "Within Capacity"
                    if item.get(
                        "within_capacity",
                        False
                    )
                    else "Over Capacity",
            }
        )

    if clearance_rows:

        st.dataframe(
            pd.DataFrame(
                clearance_rows
            ),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# QAOA
# ============================================================

st.markdown(
    '<div class="section-title">⚛️ Quantum Signal Optimization</div>',
    unsafe_allow_html=True,
)

quantum_result = safe_dict(
    qaoa.get("quantum_result")
)

signal_plan = safe_dict(
    qaoa.get("signal_plan")
)

q1, q2, q3 = st.columns(3)

with q1:

    st.metric(
        "Quantum Method",
        quantum_result.get(
            "method",
            "QAOA_AER"
        )
    )

with q2:

    st.metric(
        "Status",
        quantum_result.get(
            "status",
            "SUCCESS"
        )
    )

with q3:

    energy = quantum_result.get(
        "energy",
        0
    )

    st.metric(
        "QAOA Energy",
        f"{number(energy):.2f}"
    )


bitstring = quantum_result.get(
    "bitstring",
    ""
)

if bitstring:

    st.info(
        f"QAOA Bitstring: `{bitstring}`"
    )


signal_rows = []

for junction_id, plan in signal_plan.items():

    plan = safe_dict(plan)

    signal_rows.append(
        {
            "Junction": junction_id,
            "Plan": plan.get(
                "plan",
                "N/A"
            ),
            "Green": f"{display_number(plan.get('green', 0))} sec",
            "Red": f"{display_number(plan.get('red', 0))} sec",
        }
    )


if signal_rows:

    st.subheader("Optimized Signal Plan")

    st.dataframe(
        pd.DataFrame(signal_rows),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# BASELINE COMPARISON
# ============================================================

st.markdown(
    '<div class="section-title">📈 Traffic Control Comparison</div>',
    unsafe_allow_html=True,
)

comparison_rows = []

for controller_name, controller_metrics in controllers.items():

    controller_metrics = safe_dict(
        controller_metrics
    )

    comparison_rows.append(
        {
            "Controller": controller_name,
            "Average Waiting (sec)": display_number(
                controller_metrics.get(
                    "average_waiting_time",
                    0
                )
            ),
            "Total Queue": display_number(
                controller_metrics.get(
                    "total_queue",
                    0
                )
            ),
            "Throughput": display_number(
                controller_metrics.get(
                    "throughput",
                    0
                )
            ),
            "Emergency Travel (sec)": display_number(
                controller_metrics.get(
                    "emergency_travel_time",
                    0
                )
            ),
            "Fuel": display_number(
                controller_metrics.get(
                    "fuel",
                    0
                )
            ),
            "CO₂": display_number(
                controller_metrics.get(
                    "co2",
                    0
                )
            ),
        }
    )


if comparison_rows:

    st.dataframe(
        pd.DataFrame(
            comparison_rows
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Metrics shown are from the current simulation run."
    )


# ============================================================
# ENVIRONMENTAL METRICS
# ============================================================

st.markdown(
    '<div class="section-title">🌱 Environmental Impact</div>',
    unsafe_allow_html=True,
)

environment_metrics = safe_dict(
    controllers.get(
        "Quantum-Hybrid Prototype"
    )
)

fuel = environment_metrics.get(
    "fuel",
    0
)

co2 = environment_metrics.get(
    "co2",
    0
)

emergency_time = environment_metrics.get(
    "emergency_travel_time",
    0
)

a1, a2, a3 = st.columns(3)

with a1:
    st.metric(
        "Fuel Estimate",
        f"{display_number(fuel)}"
    )

with a2:
    st.metric(
        "CO₂ Estimate",
        f"{display_number(co2)}"
    )

with a3:
    st.metric(
        "Emergency Travel Time",
        f"{display_number(emergency_time)} sec"
    )


# ============================================================
# AUDIT
# ============================================================

st.markdown(
    '<div class="section-title">🔐 Decision Audit</div>',
    unsafe_allow_html=True,
)

audit_valid = result.get(
    "audit_valid",
    False
)

if audit_valid:

    st.success(
        "AUDIT CHAIN VALID — SHA-256 hash chain verified."
    )

else:

    st.warning(
        "Audit chain could not be verified."
    )


if audit:

    audit_cols = st.columns(4)

    with audit_cols[0]:
        st.metric(
            "Audit Index",
            audit.get(
                "index",
                0
            )
        )

    with audit_cols[1]:
        st.metric(
            "Decision",
            audit.get(
                "decision_type",
                "N/A"
            )
        )

    with audit_cols[2]:
        st.metric(
            "Scenario",
            audit.get(
                "scenario",
                scenario_value
            )
        )

    with audit_cols[3]:
        st.metric(
            "Chain",
            "VALID"
            if audit_valid
            else "CHECK"
        )


# ============================================================
# INTEGRATION STATUS
# ============================================================

st.markdown(
    '<div class="section-title">🔗 Integration Status</div>',
    unsafe_allow_html=True,
)

i1, i2, i3, i4 = st.columns(4)

with i1:
    st.success("Shree Prediction")

with i2:
    st.success("San Emergency")

with i3:
    st.success("Nila QAOA")

with i4:
    st.success("SHA-256 Audit")


st.divider()

st.caption(
    "Q-TRAFFIC — Hybrid Quantum-Classical Adaptive Urban Traffic Optimization Prototype"
)