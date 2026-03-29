import pandas as pd

# Load parsed logs
df = pd.read_json("parsed_logs.json")

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Create 2-minute windows
df["window"] = df["timestamp"].dt.floor("2min")

# Create numeric flags
df["is_failed"] = (df["event"] == "failed_login").astype(int)
df["is_success"] = (df["event"] == "successful_login").astype(int)

# Group by IP and time window
features = df.groupby(["ip", "window"]).agg(
    failed_count=("is_failed", "sum"),
    success_count=("is_success", "sum"),
    unique_users=("user", "nunique")
).reset_index()

print(features)

# Save features
features.to_csv("features.csv", index=False)

print("\nFeature dataset created successfully.")
