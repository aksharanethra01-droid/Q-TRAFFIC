import pandas as pd
import plotly.express as px
import streamlit as st

def render_metrics(df):
    if df.empty:
        st.info("Run the demo to create metrics.")
        return
    for col, title in [("average_waiting_time","Waiting"),("queue_length","Queue"),
                       ("throughput","Throughput"),("fuel_litres_simulation_estimate","Fuel"),
                       ("co2_kg_simulation_estimate","CO2"),("emergency_delay","Emergency delay")]:
        if col in df:
            fig=px.line(df, x="time", y=col, title=title, markers=True)
            st.plotly_chart(fig, use_container_width=True)
