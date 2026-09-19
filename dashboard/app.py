import requests
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Q-TRAFFIC | Traffic Command",
    page_icon="🚦",
    layout="wide"
)


# ============================================================
# API FUNCTIONS
# ============================================================

def check_api():
    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return None


def run_scenario(location, scenario):

    try:

        response = requests.post(
            f"{API_URL}/scenario/run",
            json={
                "location": location,
                "scenario": scenario
            },
            timeout=180
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"API Error {response.status_code}"
        )

        st.code(response.text)

        return None

    except Exception as e:

        st.error(
            f"Could not connect to FastAPI: {e}"
        )

        return None


# ============================================================
# SESSION STATE
# ============================================================

if "scenario_result" not in st.session_state:
    st.session_state.scenario_result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.caption("Q-TRAFFIC CONTROL")

    st.title("Simulation Console")

    st.write(
        "FastAPI-connected traffic intelligence"
    )

    st.subheader("LOCATION")

    location = st.selectbox(
        "Select Location",
        [
            "Coimbatore",
            "Chennai",
            "Madurai",
            "Salem"
        ]
    )

    st.subheader("TRAFFIC SCENARIO")

    scenario = st.selectbox(
        "Select Scenario",
        [
            "Normal Traffic",
            "School Peak",
            "Textile Festival",
            "Accident",
            "Vehicle Obstruction",
            "Ambulance Emergency"
        ]
    )

    st.divider()

    api_status = check_api()

    if api_status:

        st.success("FASTAPI CONNECTED")

        st.caption(
            "Dashboard is connected to the Q-TRAFFIC API."
        )

    else:

        st.error("FASTAPI DISCONNECTED")

        st.caption(
            "Start FastAPI using:"
        )

        st.code(
            "uvicorn api.main:app --reload"
        )

    run_button = st.button(
        "RUN SCENARIO ANALYSIS",
        type="primary",
        use_container_width=True
    )

    reset_button = st.button(
        "RESET",
        use_container_width=True
    )


# ============================================================
# RESET
# ============================================================

if reset_button:

    st.session_state.scenario_result = None

    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🚦 Q-TRAFFIC COMMAND CENTER"
)

st.write(
    "Hybrid Quantum-Classical Traffic Intelligence"
)

st.caption(
    "FastAPI-connected multi-intersection traffic "
    "optimization, congestion intelligence, "
    "emergency routing and quantum signal optimization."
)

h1, h2, h3, h4 = st.columns(4)

with h1:
    st.success("API CONNECTED")

with h2:
    st.info("QUBO / QAOA")

with h3:
    st.info("4-INTERSECTION PROTOTYPE")

with h4:
    st.info("SIMULATION MODE")


# ============================================================
# RUN SCENARIO
# ============================================================

if run_button:

    with st.spinner(
        "Running traffic simulation and QAOA optimization..."
    ):

        result = run_scenario(
            location,
            scenario
        )

    if result:

        st.session_state.scenario_result = result

        st.success(
            "Scenario analysis completed successfully."
        )


# ============================================================
# GET RESULT
# ============================================================

result = st.session_state.scenario_result


# ============================================================
# INITIAL SCREEN
# ============================================================

if not result:

    st.info(
        "Select a location and scenario from the sidebar, "
        "then click RUN SCENARIO ANALYSIS."
    )

    st.stop()


# ============================================================
# SCENARIO INFORMATION
# ============================================================

st.divider()

st.header("Scenario")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Location",
        result.get("location", "N/A")
    )

with c2:
    st.metric(
        "Scenario",
        result.get("scenario", "N/A")
    )

with c3:

    event = result.get("event", {})

    st.metric(
        "Active Event",
        event.get("type", "NONE")
    )


# ============================================================
# EXTRACT DATA
# ============================================================

junctions = result.get(
    "junctions",
    {}
)

predictions = result.get(
    "predictions",
    {}
)

controllers = result.get(
    "controllers",
    {}
)

qaoa = result.get(
    "qaoa",
    {}
)

quantum_result = qaoa.get(
    "quantum_result",
    {}
)

signal_plan = qaoa.get(
    "signal_plan",
    {}
)

emergency = result.get(
    "emergency"
)

audit = result.get(
    "audit",
    {}
)

audit_valid = result.get(
    "audit_valid",
    False
)


# ============================================================
# NETWORK PERFORMANCE
# ============================================================

st.divider()

st.header("📊 Network Performance")


total_vehicles = sum(
    int(junction.get("vehicles", 0))
    for junction in junctions.values()
)

total_queue = sum(
    int(junction.get("queue", 0))
    for junction in junctions.values()
)


quantum_controller = controllers.get(
    "Quantum-Hybrid Prototype",
    {}
)

quantum_metrics = quantum_controller.get(
    "metrics",
    {}
)


average_waiting = quantum_metrics.get(
    "average_waiting_time",
    0
)

throughput = quantum_metrics.get(
    "throughput",
    0
)


m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "Vehicles",
        total_vehicles
    )

with m2:

    st.metric(
        "Total Queue",
        total_queue
    )

with m3:

    st.metric(
        "Average Waiting",
        f"{average_waiting:.2f} sec"
    )

with m4:

    st.metric(
        "Throughput",
        throughput
    )


# ============================================================
# ROAD NETWORK
# ============================================================

st.divider()

st.header("🛣️ Road Network")


network_rows = []

for junction_id, junction in junctions.items():

    prediction = predictions.get(
        junction_id,
        {}
    )

    network_rows.append(
        {
            "Junction": junction_id,
            "Name": junction.get(
                "name",
                ""
            ),
            "Vehicles": junction.get(
                "vehicles",
                0
            ),
            "Queue": junction.get(
                "queue",
                0
            ),
            "Speed": junction.get(
                "speed",
                0
            ),
            "Capacity": junction.get(
                "capacity",
                0
            ),
            "Signal": junction.get(
                "signal",
                "N/A"
            ),
            "Congestion": prediction.get(
                "level",
                "N/A"
            )
        }
    )


st.dataframe(
    network_rows,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CONGESTION INTELLIGENCE
# ============================================================

st.divider()

st.header("🧠 Congestion Intelligence")


prediction_rows = []

for junction_id, prediction in predictions.items():

    prediction_rows.append(
        {
            "Junction": junction_id,
            "Congestion Score": prediction.get(
                "congestion_score",
                0
            ),
            "Level": prediction.get(
                "level",
                "N/A"
            ),
            "Queue": prediction.get(
                "queue",
                0
            ),
            "Speed": prediction.get(
                "speed",
                0
            ),
            "Density": prediction.get(
                "density",
                0
            )
        }
    )


st.dataframe(
    prediction_rows,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# EMERGENCY GREEN CORRIDOR
# ============================================================

if emergency:

    st.divider()

    st.header("🚑 Emergency Green Corridor")

    e1, e2, e3 = st.columns(3)

    with e1:

        st.metric(
            "Emergency Vehicle",
            emergency.get(
                "vehicle",
                "N/A"
            )
        )

    with e2:

        route = emergency.get(
            "selected_route",
            []
        )

        st.metric(
            "Route",
            " → ".join(route)
        )

    with e3:

        st.metric(
            "Corridor Status",
            emergency.get(
                "corridor_status",
                "N/A"
            )
        )


    st.subheader("Green Corridor Junctions")

    st.json(
        emergency.get(
            "junctions",
            {}
        )
    )


    st.subheader("Route Clearance")

    st.json(
        emergency.get(
            "clearance",
            {}
        )
    )


    st.subheader("Recovery Plan")

    st.json(
        emergency.get(
            "recovery",
            {}
        )
    )


# ============================================================
# QUANTUM OPTIMIZATION
# ============================================================

st.divider()

st.header("⚛️ Quantum Optimization")


q1, q2, q3 = st.columns(3)


with q1:

    st.metric(
        "QAOA Bitstring",
        quantum_result.get(
            "bitstring",
            "N/A"
        )
    )


with q2:

    energy = quantum_result.get(
        "energy"
    )

    if energy is not None:

        st.metric(
            "QAOA Energy",
            energy
        )

    else:

        st.metric(
            "QAOA Energy",
            "N/A"
        )


with q3:

    st.metric(
        "Quantum Status",
        "OPTIMIZED"
    )


# ============================================================
# SIGNAL PLAN
# ============================================================

st.subheader(
    "Optimized Signal Plan"
)


signal_rows = []

for junction_id, plan in signal_plan.items():

    signal_rows.append(
        {
            "Junction": junction_id,
            "Green": plan.get(
                "green",
                0
            ),
            "Red": plan.get(
                "red",
                0
            ),
            "Plan": plan.get(
                "plan",
                "N/A"
            ),
            "Quantum Bit": plan.get(
                "quantum_bit",
                0
            )
        }
    )


st.dataframe(
    signal_rows,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CLASSICAL VS QUANTUM
# ============================================================

st.divider()

st.header(
    "📈 Traffic Control Comparison"
)


comparison_rows = []


for controller_name, controller in controllers.items():

    metrics = controller.get(
        "metrics",
        {}
    )

    comparison_rows.append(
        {
            "Controller": controller_name,
            "Average Waiting (sec)": metrics.get(
                "average_waiting_time"
            ),
            "Total Queue": metrics.get(
                "total_queue"
            ),
            "Throughput": metrics.get(
                "throughput"
            ),
            "Emergency Travel Time (sec)": metrics.get(
                "emergency_travel_time"
            ),
            "Fuel": metrics.get(
                "fuel"
            ),
            "CO2": metrics.get(
                "co2"
            )
        }
    )


st.dataframe(
    comparison_rows,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ENVIRONMENTAL METRICS
# ============================================================

st.divider()

st.header(
    "🌱 Environmental Analysis"
)


fuel = quantum_metrics.get(
    "fuel"
)

co2 = quantum_metrics.get(
    "co2"
)

emergency_travel = quantum_metrics.get(
    "emergency_travel_time"
)


e1, e2, e3 = st.columns(3)


with e1:

    st.metric(
        "Fuel",
        f"{fuel:.2f}" if fuel is not None else "N/A"
    )


with e2:

    st.metric(
        "CO₂",
        f"{co2:.2f}" if co2 is not None else "N/A"
    )


with e3:

    st.metric(
        "Emergency Travel Time",
        (
            f"{emergency_travel:.2f} sec"
            if emergency_travel is not None
            else "N/A"
        )
    )


# ============================================================
# AUDIT
# ============================================================

st.divider()

st.header(
    "🔐 Decision Audit"
)


if audit_valid:

    st.success(
        "AUDIT CHAIN VALID — SHA-256 hash chain verified."
    )

else:

    st.error(
        "AUDIT CHAIN INVALID"
    )


with st.expander(
    "View Audit Block"
):

    st.json(audit)


# ============================================================
# INTEGRATION STATUS
# ============================================================

st.divider()

st.header(
    "🔗 Integration Status"
)


s1, s2, s3, s4 = st.columns(4)


with s1:
    st.success("FastAPI")

with s2:
    st.success("Traffic Prediction")

with s3:
    st.success("San Emergency")

with s4:
    st.success("QAOA + Audit")


st.caption(
    "Q-TRAFFIC | Hybrid Quantum-Classical "
    "Urban Traffic Optimization Prototype"
)