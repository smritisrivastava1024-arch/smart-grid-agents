# ⚡ Smart Grid Multi-Agent Load Dispatcher

An AI-powered Smart Grid Control Room Simulation that combines Machine Learning, Graph Algorithms, LangChain Agents, Weather Forecast APIs, and Interactive Dashboards to manage a renewable energy grid.

---

## Overview

This project simulates a localized smart electrical grid consisting of:

* Solar Generation
* Transformers
* Residential Loads
* Battery Storage Systems

The system uses multiple intelligent agents that cooperate to predict solar generation, dispatch backup energy, analyze faults, and generate automated technical reports.

---

## Architecture

### Agent 1 — Solar Prediction Agent

Responsible for forecasting solar generation using machine learning.

**Features**

* OpenWeather Forecast API integration
* Solar generation prediction
* Decision Tree Regressor model
* Historical telemetry training dataset

**Inputs**

* Hour of day
* Cloud cover
* Temperature

**Output**

* Predicted solar power generation

---

### Agent 2 — Load Dispatcher Agent

Responsible for maintaining grid stability.

**Features**

* Battery selection optimization
* Battery health monitoring
* Graph-based routing
* Shortest-path battery dispatch using NetworkX

When solar generation falls below operational thresholds, the dispatcher automatically routes power from the most suitable battery.

---

### Agent 3 — Safety Analysis Agent

Responsible for fault diagnosis and incident reporting.

**Features**

* LangChain integration
* Groq LLM integration
* Fault localization
* Automated incident reports

The agent analyzes:

* Voltage spikes
* Transformer overloads
* Battery overheating
* Battery discharge anomalies

and generates technical reports explaining:

* Root cause
* Safety implications
* Recommended actions

---

## Grid Topology

The electrical grid is modeled as a graph structure.

### Nodes

* Solar Panel
* Transformers
* Houses
* Battery Banks

### Edges

Transmission lines connecting all components.

Graph algorithms are used for:

* Route discovery
* Battery dispatch
* Network visualization

---

## Technologies Used

### Machine Learning

* Scikit-Learn
* Pandas

### AI / LLM

* LangChain
* Groq
* Llama 3.3 70B

### Smart Grid Modeling

* NetworkX

### Dashboard

* Streamlit

### Data Sources

* OpenWeather Forecast API

### Visualization

* Matplotlib

---

## Features

### Solar Forecasting

Predicts solar generation using:

* Weather forecast data
* Cloud cover
* Temperature

### Battery Optimization

Chooses batteries using:

* Current charge level
* Battery health
* Grid accessibility

### Battery Health Tracking

Simulates battery degradation during dispatch cycles.

### Shortest Path Routing

Computes optimal energy routes using graph algorithms.

Example:

```text
solar_panel
→ transformer_1
→ transformer_2
→ battery_1
```

### Fault Localization

Faults can occur at:

* Transformer 1
* Transformer 2
* Battery 1
* Battery 2

### AI Incident Reports

LangChain-powered fault analysis automatically generates technical incident reports.

### Interactive Dashboard

Users can:

* Select city
* Configure fault probability
* Run simulations
* Visualize battery usage
* Review fault reports

---

## Dashboard

The Streamlit dashboard provides:

* Solar generation charts
* Battery charge tracking
* Battery health monitoring
* Dispatch route visualization
* Fault report analysis
* Grid topology visualization

---

## Installation

### Clone Repository

```bash
git clone https://github.com/smritisrivastava1024-arch/smart-grid-agents.git
cd smart-grid-agents
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_openweather_api_key
```

---

## Run Simulation

```bash
python main.py
```

Run with a specific city:

```bash
python main.py --city Delhi
```

---

## Launch Dashboard

```bash
streamlit run app.py
```

---

## Example Output

```text
FAULT DETECTED at transformer_2: Voltage Spike

Agent 3 Report:
A voltage spike of 259V occurred at transformer_2,
exceeding the normal operating range.
Immediate isolation and investigation are recommended.
```

---

## Generated Files

| File                 | Description                    |
| -------------------- | ------------------------------ |
| simulation_log.csv   | Full simulation telemetry      |
| incident_reports.csv | AI-generated fault reports     |
| grid_topology.png    | Network topology visualization |

---

## Future Improvements

* Real smart-meter integration
* Reinforcement learning dispatch optimization
* Demand forecasting
* SCADA integration
* Real-time IoT telemetry
* Multi-city grid simulations

---

## Author

**Smriti Srivastava**

Electrical and Electronics Engineering Student

Focused on:

* Smart Grids
* Artificial Intelligence
* Multi-Agent Systems
* Machine Learning
* Power Systems
