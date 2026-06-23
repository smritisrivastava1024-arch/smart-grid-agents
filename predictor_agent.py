import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error

# Load the data we generated
df = pd.read_csv("sensor_data.csv")

# Features (inputs) the model will learn from
X = df[["hour_of_day", "cloud_cover", "temperature"]]

# Target (what we want to predict)
y = df["solar_output"]

# Split into training data (80%) and testing data (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = DecisionTreeRegressor(random_state=42)
model.fit(X_train, y_train)

# Test how good the model is
predictions = model.predict(X_test)
error = mean_absolute_error(y_test, predictions)

print(f"Model trained successfully!")
print(f"Average prediction error: {error:.2f} units of solar output")
print(f"\nSample predictions vs actual values:")
for i in range(5):
    print(f"Predicted: {predictions[i]:.1f} | Actual: {y_test.iloc[i]:.1f}")