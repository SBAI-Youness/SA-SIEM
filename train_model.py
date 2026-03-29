import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Load feature dataset
df = pd.read_csv("features.csv")

# Select only numeric features for ML
X = df[["failed_count", "success_count", "unique_users"]]

# Create model
model = IsolationForest(
    contamination=0.15,   # 15% anomalies (since dataset small)
    random_state=42
)

# Train model
model.fit(X)

# Predict anomalies
df["anomaly_score"] = model.decision_function(X)
df["anomaly"] = model.predict(X)  # -1 = anomaly, 1 = normal

print(df)

# Save model
joblib.dump(model, "isolation_forest_model.joblib")

print("\nModel trained and saved successfully.")
