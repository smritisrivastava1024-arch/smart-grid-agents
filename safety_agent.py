import httpx
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

http_client = httpx.Client(headers={"User-Agent": "Mozilla/5.0"})
client = Groq(api_key=os.getenv("GROQ_API_KEY"), http_client=http_client)

MODEL = "llama-3.3-70b-versatile"

def generate_incident_report(node_name, issue_type, reading_value, normal_range):
    """
    Agent 3: Takes raw technical details about a grid fault
    and generates a clear incident report explaining what happened.
    """
    prompt = f"""A fault has occurred in an electrical grid simulation.

Node affected: {node_name}
Issue type: {issue_type}
Reading at time of fault: {reading_value}
Normal expected range: {normal_range}

Write a short, clear technical incident report (3-4 sentences) explaining:
1. What happened
2. Why this reading is abnormal
3. What this could mean for grid safety

Be factual and technical, like a real control room incident log."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a grid safety analysis agent that writes clear, factual incident reports for electrical faults."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content

# Test it with a simulated voltage spike
report = generate_incident_report(
    node_name="transformer_1",
    issue_type="Voltage Spike",
    reading_value="265V",
    normal_range="220V - 240V"
)

print("=== INCIDENT REPORT ===")
print(report)