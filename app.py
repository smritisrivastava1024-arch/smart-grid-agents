import os
import subprocess
import sys

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Smart Grid Multi-Agent Dashboard",
    layout="wide"
)

st.title(" Smart Grid Multi-Agent Load Dispatcher")
st.write(" solar prediction + shortest-path battery dispatch + LangChain fault analysis")

st.sidebar.header("Simulation Controls")

city = st.sidebar.text_input("City", value="Mumbai")
fault_probability = st.sidebar.slider(
    "Fault probability per hour",
    min_value=0.0,
    max_value=0.5,
    value=0.05,
    step=0.01
)

run_button = st.sidebar.button("Run New Simulation")

if run_button:
    with st.spinner("Running smart grid simulation..."):
        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "--city",
                city,
                "--fault-probability",
                str(fault_probability)
            ],
            capture_output=True,
            text=True
        )

    if result.returncode == 0:
        st.success("Simulation completed.")
        with st.expander("Terminal Output"):
            st.code(result.stdout)
    else:
        st.error("Simulation failed.")
        st.code(result.stderr)

if not os.path.exists("simulation_log.csv"):
    st.warning("No simulation log found. Run a simulation first.")
    st.stop()

df = pd.read_csv("simulation_log.csv")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average Solar Output", f"{df['predicted_output'].mean():.1f}")
col2.metric("Battery Activations", int(df["battery_activated"].sum()))
col3.metric("Faults Detected", int(df["fault_occurred"].sum()))
col4.metric("Lowest Solar Output", f"{df['predicted_output'].min():.1f}")

st.subheader("Solar Output Over 24 Hours")
st.line_chart(df.set_index("hour")["predicted_output"])

st.subheader("Battery Charge Levels")
st.line_chart(df.set_index("hour")[["battery_1_charge", "battery_2_charge"]])

st.subheader("Battery Health")
st.line_chart(df.set_index("hour")[["battery_1_health", "battery_2_health"]])

st.subheader("Dispatch Routes")
route_df = df[df["battery_activated"] == True][
    ["hour", "selected_battery", "route_path", "predicted_output"]
]
st.dataframe(route_df, width="stretch")

st.subheader("Full Simulation Log")
st.dataframe(df, width="stretch")

if os.path.exists("incident_reports.csv"):
    incident_df = pd.read_csv("incident_reports.csv")

    st.subheader("LangChain Fault Reports")
    if len(incident_df) == 0:
        st.info("No faults occurred in this simulation.")
    else:
        st.dataframe(incident_df, width="stretch")

if os.path.exists("grid_topology.png"):
    st.subheader("Grid Network Topology")
    st.image("grid_topology.png")