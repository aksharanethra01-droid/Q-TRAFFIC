import streamlit as st
import pandas as pd

from data.schemas import TRAFFIC_STATE
from data.events import ACCIDENT_EVENT
from data.optimization import OPTIMIZATION_RESULT
from data.emergency import EMERGENCY_RESULT


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Q-TRAFFIC",
    page_icon="🚦",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🚦 Q-TRAFFIC")
st.subheader("Quantum-Assisted Urban Traffic Optimization")

st.markdown(
    "Real-time traffic monitoring, prediction, emergency routing "
    "and optimized signal control."
)


# --------------------------------------------------
# NETWORK STATUS
# --------------------------------------------------

st.header("🌐 Network Status")

col1, col2, col3, col4 = st.columns(4)

total_vehicles = sum(
    data["vehicles"]
    for data in TRAFFIC_STATE.values()
)

total_queue = sum(
    data["queue"]
    for data in TRAFFIC_STATE.values()
)

average_speed = sum(
    data["speed"]
    for data in TRAFFIC_STATE.values()
) / len(TRAFFIC_STATE)

with col1:
    st.metric(
        "Junctions",
        len(TRAFFIC_STATE)
    )

with col2:
    st.metric(
        "Vehicles",
        total_vehicles
    )

with col3:
    st.metric(
        "Total Queue",
        total_queue
    )

with col4:
    st.metric(
        "Avg Speed",
        f"{average_speed:.1f} km/h"
    )


# --------------------------------------------------
# CURRENT TRAFFIC
# --------------------------------------------------

st.header("📊 Current Traffic")

rows = []

for junction, data in TRAFFIC_STATE.items():

    rows.append({
        "Junction": junction,
        "Vehicles": data["vehicles"],
        "Queue": data["queue"],
        "Speed (km/h)": data["speed"],
        "Capacity": data["capacity"],
        "Current Signal": data["signal"]
    })

traffic_df = pd.DataFrame(rows)

st.dataframe(
    traffic_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# TRAFFIC EVENT
# --------------------------------------------------

st.header("🚨 Active Traffic Event")

st.warning(
    f"**{ACCIDENT_EVENT['type']}** detected at "
    f"**{ACCIDENT_EVENT['junction']}** "
    f"(Severity: {ACCIDENT_EVENT['severity']})"
)


# --------------------------------------------------
# OPTIMIZED SIGNAL PLAN
# --------------------------------------------------

st.header("⚛️ Optimized Signal Plan")

optimization_rows = []

for junction, plan in OPTIMIZATION_RESULT.items():

    optimization_rows.append({
        "Junction": junction,
        "Optimized Plan": plan
    })

optimization_df = pd.DataFrame(optimization_rows)

st.dataframe(
    optimization_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# EMERGENCY VEHICLE
# --------------------------------------------------

st.header("🚑 Emergency Vehicle")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Vehicle",
        EMERGENCY_RESULT["vehicle"]
    )

    st.metric(
        "Priority",
        EMERGENCY_RESULT["priority"]
    )

with col2:

    route = " → ".join(
        EMERGENCY_RESULT["route"]
    )

    st.info(
        f"**Route**\n\n"
        f"{route}\n\n"
        f"**Status:** {EMERGENCY_RESULT['status']}"
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Q-TRAFFIC | Quantum-Assisted Urban Traffic Optimization"
)