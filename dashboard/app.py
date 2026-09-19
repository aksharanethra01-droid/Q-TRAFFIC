import streamlit as st
import pandas as pd
import requests
import html


# ============================================================
# CONFIG
# ============================================================

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Q-TRAFFIC | Traffic Command",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPERS
# ============================================================

def h(value):
    return html.escape(str(value))


def ui(markup):
    st.html(markup)


def api_get(endpoint):
    response = requests.get(
        f"{API_URL}{endpoint}",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def api_post(endpoint, payload):
    response = requests.post(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


def safe_number(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def level_class(level):
    level = str(level).upper()

    if level == "CRITICAL":
        return "critical"

    if level == "HIGH":
        return "high"

    if level == "MODERATE":
        return "moderate"

    return "low"


# ============================================================
# CSS
# ============================================================

ui("""
<style>

:root {
    --bg: #06101d;
    --panel: #0c192b;
    --panel2: #10213a;
    --line: #203953;
    --text: #eef5ff;
    --muted: #8da3bf;
    --blue: #3b82f6;
    --cyan: #22d3ee;
    --green: #22c55e;
    --amber: #f59e0b;
    --orange: #f97316;
    --red: #ef4444;
}

.stApp {
    background:
        radial-gradient(
            circle at 75% 0%,
            rgba(59,130,246,.13),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            #06101d 0%,
            #07111f 100%
        );

    color: var(--text);
}

.block-container {
    max-width: 1480px;
    padding: 1.6rem 2rem 4rem 2rem;
}

[data-testid="stSidebar"] {
    background: #07111f;
    border-right: 1px solid #1c3049;
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

[data-testid="stSidebar"] .stButton button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #2e5d9c;
    background: linear-gradient(
        135deg,
        #2563eb,
        #1d4ed8
    );
    color: white;
    font-weight: 800;
    min-height: 44px;
}

.command {
    background:
        linear-gradient(
            135deg,
            #0c1b30 0%,
            #0a1628 55%,
            #102743 100%
        );

    border: 1px solid #274461;
    border-radius: 20px;
    padding: 28px 32px;
    box-shadow: 0 18px 55px rgba(0,0,0,.28);
}

.kicker {
    color: #7795b9;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 2.1px;
}

.title {
    color: #f7fbff;
    font-size: 36px;
    line-height: 1.08;
    font-weight: 950;
    margin-top: 7px;
}

.subtitle {
    color: #9cb0c8;
    font-size: 14px;
    margin-top: 8px;
}

.statuses {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 18px;
}

.status {
    border: 1px solid #294562;
    background: rgba(255,255,255,.025);
    color: #a9bdd5;
    padding: 7px 11px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: .8px;
}

.status.active {
    border-color: rgba(34,197,94,.32);
    color: #70e79a;
}

.status.quantum {
    border-color: rgba(59,130,246,.4);
    color: #8eb9ff;
}

.section-title {
    color: #e7f0fc;
    font-size: 19px;
    font-weight: 900;
    margin-top: 26px;
    margin-bottom: 8px;
}

.section-line {
    height: 1px;
    background:
        linear-gradient(
            90deg,
            #2b4968,
            transparent
        );

    margin-bottom: 14px;
}

.notice {
    border: 1px solid #29415e;
    background: rgba(13,28,47,.8);
    border-radius: 13px;
    padding: 13px 16px;
    color: #94a9c2;
    font-size: 12px;
    line-height: 1.55;
}

.notice strong {
    color: #d9e7f7;
}

.metric {
    background:
        linear-gradient(
            145deg,
            #0c1a2c,
            #0a1626
        );

    border: 1px solid #203953;
    border-radius: 15px;
    padding: 17px;
    min-height: 112px;
}

.metric-label {
    color: #7890ad;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1.1px;
    text-transform: uppercase;
}

.metric-value {
    color: #f4f8ff;
    font-size: 28px;
    font-weight: 950;
    margin-top: 7px;
}

.metric-sub {
    color: #6f86a3;
    font-size: 11px;
    margin-top: 3px;
}

.panel {
    background:
        linear-gradient(
            145deg,
            #0c192b,
            #0a1626
        );

    border: 1px solid #1f3853;
    border-radius: 17px;
    padding: 19px;
}

.panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 15px;
}

.panel-title {
    color: #eaf2fd;
    font-size: 16px;
    font-weight: 900;
}

.panel-meta {
    color: #6f87a5;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 1px;
}

.junction {
    background: #0e1d31;
    border: 1px solid #203c5b;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 10px;
}

.junction-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.junction-name {
    color: #f0f6ff;
    font-size: 14px;
    font-weight: 900;
}

.junction-id {
    color: #607a99;
    font-size: 10px;
    margin-left: 6px;
}

.badge {
    display: inline-block;
    border-radius: 999px;
    padding: 4px 8px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: .6px;
}

.badge.low {
    background: rgba(34,197,94,.11);
    color: #69e596;
}

.badge.moderate {
    background: rgba(245,158,11,.12);
    color: #f6c25d;
}

.badge.high {
    background: rgba(249,115,22,.13);
    color: #ff9c60;
}

.badge.critical {
    background: rgba(239,68,68,.13);
    color: #ff7777;
}

.grid4 {
    display: grid;
    grid-template-columns:
        repeat(4, 1fr);

    gap: 8px;
    margin-top: 12px;
}

.mini {
    background: #091627;
    border-radius: 9px;
    padding: 9px;
}

.mini-label {
    color: #617995;
    font-size: 8px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .8px;
}

.mini-value {
    color: #e7f0fc;
    font-size: 15px;
    font-weight: 900;
    margin-top: 3px;
}

.topology {
    position: relative;
    min-height: 300px;
    border-radius: 15px;

    border: 1px solid #1e3957;

    background:
        linear-gradient(
            rgba(50,78,106,.12) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(50,78,106,.12) 1px,
            transparent 1px
        ),
        #091627;

    background-size: 36px 36px;
    overflow: hidden;
}

.road-h,
.road-v {
    position: absolute;
    background: rgba(97,125,155,.13);
}

.road-h {
    left: 8%;
    right: 8%;
    height: 26px;
    top: 48%;
}

.road-v {
    top: 8%;
    bottom: 8%;
    width: 26px;
    left: 48%;
}

.topo-node {
    position: absolute;
    transform: translate(-50%, -50%);
    width: 95px;

    padding: 10px 7px;

    border-radius: 12px;
    text-align: center;

    background: #10243d;
    border: 1px solid #38618b;

    box-shadow:
        0 8px 22px rgba(0,0,0,.28);
}

.topo-node strong {
    display: block;
    color: #edf5ff;
    font-size: 12px;
}

.topo-node span {
    display: block;
    color: #7690ae;
    font-size: 8px;
    margin-top: 3px;
}

.event {
    background:
        linear-gradient(
            135deg,
            rgba(239,68,68,.13),
            rgba(127,29,29,.07)
        );

    border: 1px solid rgba(239,68,68,.34);
    border-radius: 15px;
    padding: 17px;
}

.event-label {
    color: #ff8585;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 1.2px;
}

.event-main {
    color: #fff1f1;
    font-size: 20px;
    font-weight: 950;
    margin-top: 4px;
}

.event-detail {
    color: #c79696;
    font-size: 11px;
    margin-top: 5px;
}

.corridor {
    display: flex;
    align-items: center;
    overflow-x: auto;
    padding: 7px 0;
}

.route-node {
    min-width: 115px;
    text-align: center;
    padding: 11px;
    border-radius: 11px;
    background: #10233b;
    border: 1px solid #31567d;
}

.route-node strong {
    display: block;
    color: #eff6ff;
    font-size: 12px;
}

.route-node span {
    display: block;
    color: #7891af;
    font-size: 8px;
    margin-top: 3px;
}

.route-arrow {
    color: #4e8df9;
    font-size: 20px;
    padding: 0 9px;
}

.decision {
    background:
        linear-gradient(
            135deg,
            #102844,
            #0d1b2e
        );

    border: 1px solid #31547c;
    border-radius: 16px;
    padding: 18px;
}

.decision-label {
    color: #9fc6ff;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 1.2px;
}

.decision-main {
    color: #f3f8ff;
    font-size: 19px;
    font-weight: 950;
    margin-top: 5px;
}

.decision-text {
    color: #9bb0c8;
    font-size: 12px;
    line-height: 1.55;
    margin-top: 6px;
}

.pipeline {
    display: grid;
    grid-template-columns:
        repeat(8, 1fr);

    gap: 7px;
}

.step {
    background: #0e1d31;
    border: 1px solid #203a56;
    border-radius: 10px;
    padding: 12px 7px;
    text-align: center;
}

.step-no {
    color: #54799e;
    font-size: 8px;
    font-weight: 900;
}

.step-name {
    color: #dce9f8;
    font-size: 10px;
    font-weight: 850;
    margin-top: 5px;
}

.footer-note {
    margin-top: 28px;
    color: #637b98;
    font-size: 10px;
    line-height: 1.6;
    border-top: 1px solid #1a2f47;
    padding-top: 16px;
}

</style>
""")


# ============================================================
# SESSION STATE
# ============================================================

if "api_result" not in st.session_state:
    st.session_state.api_result = None

if "api_error" not in st.session_state:
    st.session_state.api_error = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    ui("""
    <div style="
        padding:8px 0 20px;
    ">
        <div style="
            color:#6f89a8;
            font-size:10px;
            font-weight:900;
            letter-spacing:2px;
        ">
            Q-TRAFFIC CONTROL
        </div>

        <div style="
            color:#f2f7ff;
            font-size:25px;
            font-weight:950;
            margin-top:6px;
        ">
            Simulation Console
        </div>

        <div style="
            color:#617b99;
            font-size:11px;
            margin-top:6px;
        ">
            FastAPI-connected traffic intelligence
        </div>
    </div>
    """)

    try:

        location_response = api_get("/locations")

        locations = location_response.get(
            "locations",
            [
                "Coimbatore",
                "Chennai",
                "Madurai",
                "Salem"
            ]
        )

    except Exception:

        locations = [
            "Coimbatore",
            "Chennai",
            "Madurai",
            "Salem"
        ]

    try:

        scenario_response = api_get("/scenarios")

        scenarios = scenario_response.get(
            "scenarios",
            [
                "Normal Traffic",
                "School Peak",
                "Textile Festival",
                "Accident",
                "Vehicle Obstruction",
                "Ambulance Emergency"
            ]
        )

    except Exception:

        scenarios = [
            "Normal Traffic",
            "School Peak",
            "Textile Festival",
            "Accident",
            "Vehicle Obstruction",
            "Ambulance Emergency"
        ]


    selected_location = st.selectbox(
        "LOCATION",
        locations
    )


    selected_scenario = st.selectbox(
        "TRAFFIC SCENARIO",
        scenarios
    )


    ui("""
    <div style="
        height:1px;
        background:#1c3049;
        margin:20px 0;
    "></div>

    <div style="
        color:#718aa7;
        font-size:9px;
        font-weight:900;
        letter-spacing:1.4px;
    ">
        BACKEND
    </div>

    <div style="
        color:#54df91;
        font-size:13px;
        font-weight:900;
        margin-top:6px;
    ">
        FASTAPI CONNECTED
    </div>

    <div style="
        color:#667e9c;
        font-size:10px;
        line-height:1.55;
        margin-top:7px;
    ">
        Dashboard results are received from the Q-TRAFFIC API.
    </div>
    """)


    run = st.button(
        "RUN SCENARIO ANALYSIS",
        use_container_width=True
    )


    reset = st.button(
        "RESET",
        use_container_width=True
    )


    if reset:

        st.session_state.api_result = None
        st.session_state.api_error = None

        st.rerun()


    if run:

        try:

            payload = {
                "location": selected_location,
                "scenario": selected_scenario
            }

            with st.spinner(
                "Running Q-TRAFFIC pipeline..."
            ):

                result = api_post(
                    "/scenario/run",
                    payload
                )

            st.session_state.api_result = result
            st.session_state.api_error = None

        except Exception as e:

            st.session_state.api_result = None

            st.session_state.api_error = (
                str(e)
            )


# ============================================================
# HEADER
# ============================================================

ui("""
<div class="command">

    <div class="kicker">
        HYBRID QUANTUM-CLASSICAL TRAFFIC INTELLIGENCE
    </div>

    <div class="title">
        Q-TRAFFIC COMMAND CENTER
    </div>

    <div class="subtitle">
        FastAPI-connected multi-intersection traffic
        optimization, congestion intelligence,
        emergency routing and quantum signal optimization.
    </div>

    <div class="statuses">

        <div class="status active">
            API CONNECTED
        </div>

        <div class="status quantum">
            QUBO / QAOA
        </div>

        <div class="status">
            4-INTERSECTION PROTOTYPE
        </div>

        <div class="status">
            SIMULATION MODE
        </div>

    </div>

</div>
""")


# ============================================================
# NO RESULT
# ============================================================

if st.session_state.api_result is None:

    if st.session_state.api_error:

        st.error(
            "API Error: "
            + st.session_state.api_error
        )

        st.info(
            "Make sure FastAPI is running at "
            "http://127.0.0.1:8000"
        )

    else:

        ui("""
        <div class="section-title">
            Command Center
        </div>

        <div class="section-line"></div>

        <div class="notice">

            <strong>
                Ready for analysis.
            </strong>
            <br>

            Select a location and scenario,
            then click
            <strong>
                RUN SCENARIO ANALYSIS
            </strong>.

            <br><br>

            The dashboard will send the request
            to the FastAPI integration layer.

        </div>
        """)

    st.stop()


# ============================================================
# READ API RESULT
# ============================================================

result = st.session_state.api_result

location = result.get(
    "location",
    "Unknown"
)

scenario = result.get(
    "scenario",
    "Unknown"
)

event = result.get(
    "event",
    {}
)

traffic_state = result.get(
    "traffic_state",
    {}
)

predictions = result.get(
    "prediction",
    {}
)

emergency = result.get(
    "emergency"
)

quantum = result.get(
    "quantum",
    {}
)

signal_plan = result.get(
    "signal_plan",
    {}
)

metrics = result.get(
    "metrics",
    {}
)


# ============================================================
# SCENARIO OVERVIEW
# ============================================================

event_type = event.get(
    "type",
    "NONE"
)

ui(f"""
<div class="notice">

    <strong>
        {h(location)}
    </strong>

    &nbsp; / &nbsp;

    <strong>
        {h(scenario)}
    </strong>

    <br>

    Event:
    <strong>
        {h(event_type)}
    </strong>

</div>
""")


# ============================================================
# NETWORK METRICS
# ============================================================

ui("""
<div class="section-title">
    Network Performance
</div>

<div class="section-line"></div>
""")


total_vehicles = sum(
    safe_number(data.get("vehicles"))
    for data in traffic_state.values()
)

total_queue = sum(
    safe_number(data.get("queue"))
    for data in traffic_state.values()
)

average_speed = (

    sum(
        safe_number(data.get("speed"))
        for data in traffic_state.values()
    )
    / len(traffic_state)

    if traffic_state
    else 0
)


average_wait = safe_number(
    metrics.get(
        "average_waiting_time"
    )
)

throughput = safe_number(
    metrics.get(
        "throughput"
    )
)

fuel = metrics.get(
    "fuel"
)

co2 = metrics.get(
    "co2"
)

emergency_travel_time = metrics.get(
    "emergency_travel_time"
)


m1, m2, m3, m4 = st.columns(4)


with m1:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            Vehicles
        </div>

        <div class="metric-value">
            {int(total_vehicles)}
        </div>

        <div class="metric-sub">
            Simulated network state
        </div>

    </div>
    """)


with m2:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            Total Queue
        </div>

        <div class="metric-value">
            {int(total_queue)}
        </div>

        <div class="metric-sub">
            Vehicles waiting
        </div>

    </div>
    """)


with m3:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            Average Waiting
        </div>

        <div class="metric-value">
            {average_wait:.2f}
        </div>

        <div class="metric-sub">
            seconds
        </div>

    </div>
    """)


with m4:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            Throughput
        </div>

        <div class="metric-value">
            {int(throughput)}
        </div>

        <div class="metric-sub">
            simulated vehicles
        </div>

    </div>
    """)


# ============================================================
# ROAD NETWORK
# ============================================================

ui("""
<div class="section-title">
    Road Network
</div>

<div class="section-line"></div>
""")


left, right = st.columns(
    [1.4, 1],
    gap="large"
)


with left:

    positions = {
        "J1": (22, 48),
        "J2": (50, 25),
        "J3": (78, 48),
        "J4": (50, 74),
    }

    nodes = ""

    for junction, data in traffic_state.items():

        x, y = positions.get(
            junction,
            (50, 50)
        )

        prediction = predictions.get(
            junction,
            {}
        )

        level = str(
            prediction.get(
                "level",
                "LOW"
            )
        ).upper()

        border = {

            "CRITICAL": "#ef4444",

            "HIGH": "#f97316",

            "MODERATE": "#f59e0b",

            "LOW": "#22c55e"

        }.get(
            level,
            "#38618b"
        )

        nodes += f"""
        <div
            class="topo-node"
            style="
                left:{x}%;
                top:{y}%;
                border-color:{border};
            "
        >

            <strong>
                {h(junction)}
            </strong>

            <span>
                {h(data.get("name", "Intersection"))}
            </span>

        </div>
        """


    ui(f"""
    <div class="topology">

        <div class="road-h"></div>
        <div class="road-v"></div>

        {nodes}

    </div>
    """)


with right:

    if event_type == "NONE":

        ui("""
        <div class="panel">

            <div class="panel-head">

                <div class="panel-title">
                    Event Monitor
                </div>

                <div class="panel-meta">
                    NORMAL
                </div>

            </div>

            <div style="
                color:#71e69a;
                font-size:20px;
                font-weight:900;
            ">
                NETWORK STABLE
            </div>

            <div style="
                color:#7890ad;
                font-size:12px;
                margin-top:8px;
            ">
                No active disruption.
            </div>

        </div>
        """)

    else:

        ui(f"""
        <div class="event">

            <div class="event-label">
                ACTIVE EVENT
            </div>

            <div class="event-main">
                {h(event_type.replace("_", " "))}
            </div>

            <div class="event-detail">

                Junction:
                {h(event.get("junction") or "Network")}

                <br>

                Severity:
                {h(event.get("severity") or "ACTIVE")}

            </div>

        </div>
        """)


# ============================================================
# TRAFFIC + PREDICTION
# ============================================================

ui("""
<div class="section-title">
    Traffic & Congestion Intelligence
</div>

<div class="section-line"></div>
""")


left, right = st.columns(
    [1.25, 1],
    gap="large"
)


with left:

    for junction, data in traffic_state.items():

        prediction = predictions.get(
            junction,
            {}
        )

        level = str(
            prediction.get(
                "level",
                "LOW"
            )
        ).upper()

        score = safe_number(
            prediction.get(
                "congestion_score",
                0
            )
        )

        badge = level_class(
            level
        )

        ui(f"""
        <div class="junction">

            <div class="junction-top">

                <div>

                    <span class="junction-name">
                        {h(data.get("name", junction))}
                    </span>

                    <span class="junction-id">
                        {h(junction)}
                    </span>

                </div>

                <div>

                    <span class="badge {badge}">
                        {h(level)}
                    </span>

                </div>

            </div>


            <div class="grid4">

                <div class="mini">

                    <div class="mini-label">
                        Vehicles
                    </div>

                    <div class="mini-value">
                        {data.get("vehicles", 0)}
                    </div>

                </div>


                <div class="mini">

                    <div class="mini-label">
                        Queue
                    </div>

                    <div class="mini-value">
                        {data.get("queue", 0)}
                    </div>

                </div>


                <div class="mini">

                    <div class="mini-label">
                        Speed
                    </div>

                    <div class="mini-value">
                        {data.get("speed", 0)} km/h
                    </div>

                </div>


                <div class="mini">

                    <div class="mini-label">
                        Score
                    </div>

                    <div class="mini-value">
                        {score:.2f}
                    </div>

                </div>

            </div>

        </div>
        """)


with right:

    rows = []

    for junction, prediction in predictions.items():

        rows.append({

            "Junction":
                junction,

            "Congestion":
                round(
                    safe_number(
                        prediction.get(
                            "congestion_score",
                            0
                        )
                    ),
                    2
                ),

            "Level":
                str(
                    prediction.get(
                        "level",
                        "LOW"
                    )
                ).upper(),

        })


    prediction_df = pd.DataFrame(
        rows
    )


    st.dataframe(
        prediction_df,
        use_container_width=True,
        hide_index=True
    )


    if not prediction_df.empty:

        st.bar_chart(
            prediction_df.set_index(
                "Junction"
            )[["Congestion"]],
            height=230
        )


# ============================================================
# EMERGENCY GREEN CORRIDOR
# ============================================================

if emergency:

    ui("""
    <div class="section-title">
        Emergency Green Corridor
    </div>

    <div class="section-line"></div>
    """)


    route = emergency.get(
        "route",
        []
    )


    corridor = ""

    for index, junction in enumerate(route):

        data = traffic_state.get(
            junction,
            {}
        )

        corridor += f"""
        <div class="route-node">

            <strong>
                {h(junction)}
            </strong>

            <span>
                {h(data.get("name", "Intersection"))}
            </span>

        </div>
        """


        if index < len(route) - 1:

            corridor += """
            <div class="route-arrow">
                →
            </div>
            """


    ui(f"""
    <div class="panel">

        <div class="panel-head">

            <div>

                <div class="panel-title">
                    🚑 {h(emergency.get("vehicle", "AMB01"))}
                </div>

                <div class="panel-meta">
                    EMERGENCY ROUTE
                </div>

            </div>

            <span class="badge critical">
                GREEN CORRIDOR ACTIVE
            </span>

        </div>


        <div class="corridor">

            {corridor}

        </div>


        <div style="
            color:#7891af;
            font-size:11px;
            margin-top:10px;
        ">

            Start:
            {h(emergency.get("start", "J1"))}

            &nbsp;&nbsp;

            Destination:
            {h(emergency.get("destination", "J4"))}

            &nbsp;&nbsp;

            Priority:
            {h(emergency.get("priority", "HIGH"))}

        </div>

    </div>
    """)


# ============================================================
# QUANTUM OPTIMIZATION
# ============================================================

ui("""
<div class="section-title">
    Quantum Optimization
</div>

<div class="section-line"></div>
""")


q1, q2 = st.columns(
    2,
    gap="large"
)


with q1:

    bitstring = quantum.get(
        "bitstring",
        "N/A"
    )

    energy = quantum.get(
        "energy",
        "N/A"
    )


    ui(f"""
    <div class="decision">

        <div class="decision-label">
            QUANTUM RESULT
        </div>

        <div class="decision-main">
            Bitstring: {h(bitstring)}
        </div>

        <div class="decision-text">

            QUBO energy:
            <strong>
                {h(energy)}
            </strong>

            <br><br>

            The quantum result is received
            directly from the FastAPI optimization
            endpoint.

        </div>

    </div>
    """)


with q2:

    reference = quantum.get(
        "reference_solution",
        {}
    )

    reference_bitstring = reference.get(
        "bitstring",
        "N/A"
    )

    reference_energy = reference.get(
        "energy",
        "N/A"
    )


    ui(f"""
    <div class="decision">

        <div class="decision-label">
            REFERENCE SOLUTION
        </div>

        <div class="decision-main">
            {h(reference_bitstring)}
        </div>

        <div class="decision-text">

            Reference energy:
            <strong>
                {h(reference_energy)}
            </strong>

            <br><br>

            This provides a small-problem
            validation reference for the
            quantum-simulation result.

        </div>

    </div>
    """)


# ============================================================
# SIGNAL PLAN
# ============================================================

ui("""
<div class="section-title">
    Optimized Signal Plan
</div>

<div class="section-line"></div>
""")


signal_rows = []


for junction, plan in signal_plan.items():

    signal_rows.append({

        "Junction":
            junction,

        "Green":
            plan.get(
                "green",
                "-"
            ),

        "Red":
            plan.get(
                "red",
                "-"
            ),

        "Plan":
            plan.get(
                "plan",
                "-"
            ),

        "Quantum Bit":
            plan.get(
                "quantum_bit",
                "-"
            ),

    })


signal_df = pd.DataFrame(
    signal_rows
)


st.dataframe(
    signal_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ENVIRONMENTAL METRICS
# ============================================================

ui("""
<div class="section-title">
    Environmental & Emergency Metrics
</div>

<div class="section-line"></div>
""")


e1, e2, e3, e4 = st.columns(4)


with e1:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            Fuel
        </div>

        <div class="metric-value">
            {h(fuel if fuel is not None else "N/A")}
        </div>

        <div class="metric-sub">
            litres
        </div>

    </div>
    """)


with e2:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            CO₂
        </div>

        <div class="metric-value">
            {h(co2 if co2 is not None else "N/A")}
        </div>

        <div class="metric-sub">
            kg
        </div>

    </div>
    """)


with e3:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            Emergency Travel
        </div>

        <div class="metric-value">
            {h(
                emergency_travel_time
                if emergency_travel_time is not None
                else "N/A"
            )}
        </div>

        <div class="metric-sub">
            seconds
        </div>

    </div>
    """)


with e4:

    ui(f"""
    <div class="metric">

        <div class="metric-label">
            Average Speed
        </div>

        <div class="metric-value">
            {average_speed:.1f}
        </div>

        <div class="metric-sub">
            km/h
        </div>

    </div>
    """)


# ============================================================
# CLASSICAL BASELINE
# ============================================================

ui("""
<div class="section-title">
    Classical Baseline
</div>

<div class="section-line"></div>
""")


fixed_rows = []

adaptive_rows = []


for junction, data in traffic_state.items():

    fixed_rows.append({

        "Junction":
            junction,

        "Green":
            30,

        "Red":
            30

    })


    queue = safe_number(
        data.get("queue")
    )


    if queue >= 20:

        green = 50

    elif queue >= 10:

        green = 45

    else:

        green = 30


    adaptive_rows.append({

        "Junction":
            junction,

        "Green":
            green,

        "Red":
            60 - green

    })


base1, base2 = st.columns(
    2,
    gap="large"
)


with base1:

    ui("""
    <div class="panel">

        <div class="panel-head">

            <div class="panel-title">
                Fixed-Time
            </div>

            <div class="panel-meta">
                CLASSICAL
            </div>

        </div>

    """)

    st.dataframe(
        pd.DataFrame(fixed_rows),
        use_container_width=True,
        hide_index=True
    )

    ui("</div>")


with base2:

    ui("""
    <div class="panel">

        <div class="panel-head">

            <div class="panel-title">
                Rule-Based Adaptive
            </div>

            <div class="panel-meta">
                CLASSICAL
            </div>

        </div>

    """)

    st.dataframe(
        pd.DataFrame(adaptive_rows),
        use_container_width=True,
        hide_index=True
    )

    ui("</div>")


# ============================================================
# ACTUAL QAOA METRICS
# ============================================================

ui("""
<div class="section-title">
    Q-TRAFFIC Performance Result
</div>

<div class="section-line"></div>
""")


performance_rows = [

    {
        "Metric":
            "Average Waiting Time",

        "Value":
            metrics.get(
                "average_waiting_time",
                "N/A"
            ),

        "Unit":
            "seconds"
    },

    {
        "Metric":
            "Total Queue",

        "Value":
            metrics.get(
                "total_queue",
                "N/A"
            ),

        "Unit":
            "vehicles"
    },

    {
        "Metric":
            "Throughput",

        "Value":
            metrics.get(
                "throughput",
                "N/A"
            ),

        "Unit":
            "vehicles"
    },

    {
        "Metric":
            "Fuel",

        "Value":
            metrics.get(
                "fuel",
                "N/A"
            ),

        "Unit":
            "litres"
    },

    {
        "Metric":
            "CO₂",

        "Value":
            metrics.get(
                "co2",
                "N/A"
            ),

        "Unit":
            "kg"
    },

]


if emergency:

    performance_rows.append({

        "Metric":
            "Emergency Travel Time",

        "Value":
            metrics.get(
                "emergency_travel_time",
                "N/A"
            ),

        "Unit":
            "seconds"

    })


st.dataframe(
    pd.DataFrame(
        performance_rows
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# IMPORTANT DISCLAIMER
# ============================================================

ui("""
<div class="notice">

    <strong>
        Prototype / simulation notice:
    </strong>

    All displayed traffic, fuel, CO₂ and performance
    values are generated from the current Q-TRAFFIC
    simulation pipeline. They are not live traffic
    measurements.

    <br><br>

    Do not claim a percentage improvement over
    classical methods until all controllers have been
    evaluated under the same simulation conditions.

</div>
""")


# ============================================================
# INTEGRATION STATUS
# ============================================================

ui("""
<div class="section-title">
    Integration Status
</div>

<div class="section-line"></div>
""")


integration = [

    {
        "Module":
            "FastAPI",

        "Status":
            "CONNECTED"
    },

    {
        "Module":
            "Traffic Prediction",

        "Status":
            "CONNECTED"
    },

    {
        "Module":
            "Emergency Routing",

        "Status":
            "CONNECTED"
            if emergency
            else "READY"
    },

    {
        "Module":
            "QUBO / QAOA",

        "Status":
            "CONNECTED"
    },

    {
        "Module":
            "Signal Plan",

        "Status":
            "CONNECTED"
    },

    {
        "Module":
            "Simulation Metrics",

        "Status":
            "CONNECTED"
    },

    {
        "Module":
            "Streamlit Dashboard",

        "Status":
            "CONNECTED"
    },

    {
        "Module":
            "Blockchain Audit",

        "Status":
            "NEXT"
    }

]


st.dataframe(
    pd.DataFrame(
        integration
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# PIPELINE
# ============================================================

ui("""
<div class="section-title">
    Q-TRAFFIC Decision Pipeline
</div>

<div class="section-line"></div>

<div class="panel">

    <div class="pipeline">

        <div class="step">
            <div class="step-no">01</div>
            <div class="step-name">
                Scenario
            </div>
        </div>

        <div class="step">
            <div class="step-no">02</div>
            <div class="step-name">
                Prediction
            </div>
        </div>

        <div class="step">
            <div class="step-no">03</div>
            <div class="step-name">
                Emergency
            </div>
        </div>

        <div class="step">
            <div class="step-no">04</div>
            <div class="step-name">
                QUBO / QAOA
            </div>
        </div>

        <div class="step">
            <div class="step-no">05</div>
            <div class="step-name">
                Signals
            </div>
        </div>

        <div class="step">
            <div class="step-no">06</div>
            <div class="step-name">
                Simulation
            </div>
        </div>

        <div class="step">
            <div class="step-no">07</div>
            <div class="step-name">
                Metrics
            </div>
        </div>

        <div class="step">
            <div class="step-no">08</div>
            <div class="step-name">
                Dashboard
            </div>
        </div>

    </div>

</div>
""")


# ============================================================
# FOOTER
# ============================================================

ui(f"""
<div class="footer-note">

    Q-TRAFFIC | {h(location)} | {h(scenario)}

    <br>

    Dashboard data is received through
    FastAPI at {h(API_URL)}.

    <br>

    Traffic values are simulated prototype values,
    not live traffic data.

</div>
""")