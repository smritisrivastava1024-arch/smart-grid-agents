import pandas as pd
import numpy as np

np.random.seed(42)  # makes results reproducible

def generate_sensor_data(hours=500):
    timestamps = pd.date_range(start="2026-01-01", periods=hours, freq="h")
    
    # Simulate cloud cover (0-100%) with some randomness
    cloud_cover = np.random.randint(0, 100, size=hours)
    
    # Simulate temperature (affects panel efficiency slightly)
    temperature = np.random.normal(25, 8, size=hours).round(1)
    
    # Simulate hour of day (0-23) - solar generation depends heavily on this
    hour_of_day = [t.hour for t in timestamps]
    
    # Simulate actual solar output based on realistic rules:
    # - No sun at night (hour < 6 or hour > 19)
    # - Cloud cover reduces output
    # - Some random noise
    solar_output = []
    for i in range(hours):
        if hour_of_day[i] < 6 or hour_of_day[i] > 19:
            output = 0  # nighttime
        else:
            base_output = 100 - cloud_cover[i] * 0.8
            noise = np.random.normal(0, 5)
            output = max(0, base_output + noise)
        solar_output.append(round(output, 1))
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "hour_of_day": hour_of_day,
        "cloud_cover": cloud_cover,
        "temperature": temperature,
        "solar_output": solar_output
    })
    
    return df

# Generate and save the data
df = generate_sensor_data()
df.to_csv("sensor_data.csv", index=False)
print(df.head(10))
print(f"\nGenerated {len(df)} rows of sensor data, saved to sensor_data.csv")