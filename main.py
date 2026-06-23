import argparse
import csv
import os
import random
from datetime import datetime

import networkx as nx
import pandas as pd
import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

llm = ChatGroq(
    model=MODEL,
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

grid = {
    "solar_panel": ["transformer_1"],
    "transformer_1": ["solar_panel", "transformer_2", "house_1", "house_2"],
    "transformer_2": ["transformer_1", "house_3", "house_4", "battery_1", "battery_2"],
    "house_1": ["transformer_1"],
    "house_2": ["transformer_1"],
    "house_3": ["transformer_2"],
    "house_4": ["transformer_2"],
    "battery_1": ["transformer_2"],
    "battery_2": ["transformer_2"],
}

battery_state = {
    "battery_1": 80,
    "battery_2": 60,
}

battery_health = {
    "battery_1": 100.0,
    "battery_2": 100.0,
}

faultable_nodes = {
    "transformer_1": {
        "issues": ["Voltage Spike", "Transformer Overload"],
        "normal_range": "220V - 240V",
        "reading_range": (250, 280),
    },
    "transformer_2": {
        "issues": ["Voltage Spike", "Transformer Overload"],
        "normal_range": "220V - 240V",
        "reading_range": (250, 280),
    },
    "battery_1": {
        "issues": ["Battery Overheating", "Discharge Anomaly"],
        "normal_range": "25°C - 45°C",
        "reading_range": (50, 75),
    },
    "battery_2": {
        "issues": ["Battery Overheating", "Discharge Anomaly"],
        "normal_range": "25°C - 45°C",
        "reading_range": (50, 75),
    },
}


def build_graph():
    G = nx.Graph()
    for node, neighbors in grid.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)
    return G


def get_weather_forecast(city="Mumbai"):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if "list" not in data:
            raise ValueError(data)

        forecast = []
        for item in data["list"][:8]:
            forecast.append({
                "time": item["dt_txt"],
                "cloud_cover": item["clouds"]["all"],
                "temperature": item["main"]["temp"]
            })

        return forecast

    except Exception as e:
        print(f" Could not fetch forecast data: {e}. Using simulated fallback.")
        return None


def get_weather_for_hour(forecast_data, hour):
    if forecast_data:
        forecast_point = forecast_data[min(hour // 3, len(forecast_data) - 1)]
        return (
            forecast_point["cloud_cover"],
            forecast_point["temperature"],
            forecast_point["time"]
        )

    return (
        random.randint(0, 100),
        round(random.normalvariate(25, 8), 1),
        "simulated"
    )


def train_predictor():
    df = pd.read_csv("sensor_data.csv")

    X = df[["hour_of_day", "cloud_cover", "temperature"]]
    y = df["solar_output"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)

    return model


def predict_solar(model, hour_of_day, cloud_cover, temperature):
    input_df = pd.DataFrame(
        [[hour_of_day, cloud_cover, temperature]],
        columns=["hour_of_day", "cloud_cover", "temperature"]
    )
    return model.predict(input_df)[0]


def find_available_battery(battery_state, battery_health, start_node, min_charge=10, min_health=20):
    G = build_graph()
    candidates = []

    for battery in battery_state:
        if battery_state[battery] >= min_charge and battery_health[battery] >= min_health:
            path = nx.shortest_path(G, source=start_node, target=battery)
            candidates.append({
                "battery": battery,
                "path": path,
                "distance": len(path) - 1,
                "score": battery_state[battery] * 0.7 + battery_health[battery] * 0.3
            })

    if not candidates:
        return None, None

    best = max(candidates, key=lambda item: item["score"] - item["distance"])
    return best["battery"], best["path"]


def dispatch_power(predicted_output, battery_state, battery_health, threshold=20, drain_rate=5, degradation_rate=0.5):
    if predicted_output < threshold:
        battery_node, route_path = find_available_battery(
            battery_state,
            battery_health,
            "solar_panel"
        )

        if battery_node:
            battery_state[battery_node] = max(0, battery_state[battery_node] - drain_rate)
            battery_health[battery_node] = max(0, battery_health[battery_node] - degradation_rate)

            print(
                f"   Agent 2: Low solar output ({predicted_output:.1f}). "
                f"Using {battery_node}. Route: {' -> '.join(route_path)} "
                f"(charge: {battery_state[battery_node]}%, health: {battery_health[battery_node]:.1f}%)."
            )

            return True, battery_node, " -> ".join(route_path)

        print("   Agent 2: No healthy battery available — blackout risk.")
        return False, None, None

    for battery in battery_state:
        battery_state[battery] = min(100, battery_state[battery] + 2)

    print(f"   Agent 2: Solar output normal ({predicted_output:.1f}). No dispatch needed.")
    return False, None, None


def simulate_fault():
    node = random.choice(list(faultable_nodes.keys()))
    config = faultable_nodes[node]

    issue = random.choice(config["issues"])
    low, high = config["reading_range"]
    reading_value = random.randint(low, high)

    if "Voltage" in issue or "Transformer" in issue:
        reading = f"{reading_value}V"
    else:
        reading = f"{reading_value}°C"

    return node, issue, reading, config["normal_range"]


@tool
def get_grid_context(node_name: str) -> str:
    """Return grid connections for a given node."""
    connections = grid.get(node_name, [])
    return f"{node_name} is connected to: {connections}"


@tool
def get_battery_context() -> str:
    """Return current battery charge and health values."""
    return f"Battery charge: {battery_state}. Battery health: {battery_health}."


def generate_incident_report(node_name, issue_type, reading_value, normal_range):
    tools = [get_grid_context, get_battery_context]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a smart-grid safety analysis agent. "
            "Use the available tools when useful. "
            "Write concise technical incident reports."
        )
    )

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
A fault occurred in an electrical grid simulation.

Node: {node_name}
Issue: {issue_type}
Reading: {reading_value}
Normal range: {normal_range}

Use the tools if useful, then write a 3-4 sentence technical incident report explaining:
1. What happened
2. Why it is unsafe
3. Relevant grid or battery context
4. What action should be taken
"""
            }
        ]
    })

    return response["messages"][-1].content


def visualize_grid():
    import matplotlib.pyplot as plt

    G = build_graph()

    color_map = []
    for node in G.nodes():
        if "battery" in node:
            color_map.append("#FFA500")
        elif "transformer" in node:
            color_map.append("#4DA3FF")
        elif "solar" in node:
            color_map.append("#FFD700")
        else:
            color_map.append("#90EE90")

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=color_map,
        node_size=1800,
        font_size=8,
        font_weight="bold",
        edge_color="#888888"
    )

    plt.title("Smart Grid Network Topology")
    plt.savefig("grid_topology.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("Grid visualization saved to grid_topology.png")


def run_simulation(city="Mumbai", fault_probability=0.05):
    print("=" * 60)
    print("SMART GRID SIMULATION — 24 Hour Cycle")
    print("=" * 60)

    model = train_predictor()
    forecast_data = get_weather_forecast(city)

    if forecast_data:
        print(f"Using 24-hour forecast weather for {city}.")
    else:
        print("Using simulated fallback weather.")

    battery_activations = 0
    fault_count = 0
    total_output = 0
    blackout_risk_count = 0
    log_rows = []
    incident_rows = []

    for hour in range(24):
        cloud_cover, temperature, forecast_time = get_weather_for_hour(forecast_data, hour)

        predicted_output = predict_solar(model, hour, cloud_cover, temperature)
        total_output += predicted_output

        print(
            f"\nHour {hour:02d}:00 | Forecast: {forecast_time} | "
            f"Cloud: {cloud_cover}% | Temp: {temperature}°C | "
            f"Predicted solar: {predicted_output:.1f}"
        )

        battery_activated, selected_battery, route_path = dispatch_power(
            predicted_output,
            battery_state,
            battery_health
        )

        if battery_activated:
            battery_activations += 1
        elif predicted_output < 20:
            blackout_risk_count += 1

        fault_occurred = False
        fault_node = None
        fault_issue = None
        report = ""

        if random.random() < fault_probability:
            fault_count += 1
            fault_occurred = True

            fault_node, fault_issue, reading_value, normal_range = simulate_fault()

            print(f"   FAULT DETECTED at {fault_node}: {fault_issue}")

            report = generate_incident_report(
                node_name=fault_node,
                issue_type=fault_issue,
                reading_value=reading_value,
                normal_range=normal_range
            )

            print(f"  Agent 3 Report: {report}")

            incident_rows.append({
                "hour": hour,
                "node": fault_node,
                "issue": fault_issue,
                "reading": reading_value,
                "normal_range": normal_range,
                "report": report
            })

        log_rows.append({
            "hour": hour,
            "forecast_time": forecast_time,
            "cloud_cover": cloud_cover,
            "temperature": temperature,
            "predicted_output": round(predicted_output, 1),
            "battery_activated": battery_activated,
            "selected_battery": selected_battery,
            "route_path": route_path,
            "fault_occurred": fault_occurred,
            "fault_node": fault_node,
            "fault_issue": fault_issue,
            "battery_1_charge": battery_state["battery_1"],
            "battery_2_charge": battery_state["battery_2"],
            "battery_1_health": round(battery_health["battery_1"], 1),
            "battery_2_health": round(battery_health["battery_2"], 1)
        })

    print("\n" + "=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    print(f"City:                         {city}")
    print(f"Total hours simulated:        24")
    print(f"Average solar output:         {total_output / 24:.1f} units")
    print(f"Hours battery was activated:  {battery_activations}")
    print(f"Blackout risk hours:          {blackout_risk_count}")
    print(f"Faults detected:              {fault_count}")
    print(f"Final battery_1 charge:       {battery_state['battery_1']}%")
    print(f"Final battery_2 charge:       {battery_state['battery_2']}%")
    print(f"Final battery_1 health:       {battery_health['battery_1']:.1f}%")
    print(f"Final battery_2 health:       {battery_health['battery_2']:.1f}%")
    print("=" * 60)

    with open("simulation_log.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=log_rows[0].keys())
        writer.writeheader()
        writer.writerows(log_rows)

    with open("incident_reports.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["hour", "node", "issue", "reading", "normal_range", "report"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(incident_rows)

    print("\nDetailed log saved to simulation_log.csv")
    print("Incident reports saved to incident_reports.csv")

    visualize_grid()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="Mumbai")
    parser.add_argument("--fault-probability", type=float, default=0.05)
    args = parser.parse_args()

    run_simulation(city=args.city, fault_probability=args.fault_probability)