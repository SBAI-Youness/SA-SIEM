import pandas as pd
from sklearn.ensemble import IsolationForest

# Input file from the parsing step
log_file = "parsed_logs.json"

def perform_feature_engineering(df):
    """
    Converts raw log events into numerical features for the ML model.
    Groups activity by IP address.
    """
    print("Extracting behavioral features from logs...")
    
    # 1. Count total failed logins per IP
    failed_counts = df[df['event'] == 'failed_login'].groupby('ip').size().reset_index(name='failed_count')
    
    # 2. Count total successful logins per IP
    success_counts = df[df['event'] == 'successful_login'].groupby('ip').size().reset_index(name='success_count')
    
    # 3. Count unique usernames targeted by each IP
    unique_users = df.groupby('ip')['user'].nunique().reset_index(name='unique_users_targeted')
    
    # Merge all features into a single DataFrame
    features = pd.DataFrame({'ip': df['ip'].unique()})
    features = features.merge(failed_counts, on='ip', how='left').fillna(0)
    features = features.merge(success_counts, on='ip', how='left').fillna(0)
    features = features.merge(unique_users, on='ip', how='left').fillna(0)
    
    # 4. Calculate ratio of failed to total attempts
    features['total_attempts'] = features['failed_count'] + features['success_count']
    features['fail_ratio'] = features['failed_count'] / features['total_attempts']
    # Handle any potential division by zero just in case
    features['fail_ratio'] = features['fail_ratio'].fillna(0)
    
    return features

def train_and_detect(features):
    """
    Trains the Isolation Forest model and flags anomalies.
    """
    print("Training Isolation Forest model...")
    
    # Select the numerical columns for training
    X = features[['failed_count', 'success_count', 'unique_users_targeted', 'fail_ratio']]
    
    # Initialize the Isolation Forest [cite: 69]
    # contamination=0.05 means we estimate roughly 5% of the IPs might be anomalous
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    
    # Train the model and get predictions
    # Predictions: 1 = Normal, -1 = Anomaly
    features['anomaly_score'] = model.fit_predict(X)
    
    # Isolate the detected anomalies
    anomalies = features[features['anomaly_score'] == -1].copy()
    
    return anomalies

if __name__ == "__main__":
    try:
        # Load the parsed logs
        df = pd.read_json(log_file)
        
        # Run Feature Engineering
        ip_features = perform_feature_engineering(df)
        
        # Train AI and find anomalies
        detected_anomalies = train_and_detect(ip_features)
        
        print(f"\n--- AI ANOMALY DETECTION RESULTS ---")
        print(f"Total IPs analyzed: {len(ip_features)}")
        print(f"Suspicious IPs flagged: {len(detected_anomalies)}\n")
        
        if not detected_anomalies.empty:
            print("Details of anomalous behavior:")
            # Print the anomalies in a clean format
            for index, row in detected_anomalies.iterrows():
                print(f"IP: {row['ip']} | Failed: {int(row['failed_count'])} | Success: {int(row['success_count'])} | Users Targeted: {int(row['unique_users_targeted'])} | Fail Ratio: {row['fail_ratio']:.2f}")
        else:
            print("No anomalies detected in the current dataset.")
            
    except FileNotFoundError:
        print(f"Error: {log_file} not found. Please run parser.py first.")
