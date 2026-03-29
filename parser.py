import re
import pandas as pd
from datetime import datetime

# Pointing to the massive log file you just generated
log_file = "massive_auth.logs"
output_file = "parsed_logs.json"

# Regex catches newlines and correctly identifies both standard and invalid users
pattern = re.compile(
    r"([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+.*?sshd\[\d+\]:\s+(Failed|Accepted) password for (?:invalid user )?(\S+) from\s+([\d\.]+)"
)

data = []
current_year = 2026

print(f"Reading and parsing '{log_file}'...")
print("This might take a moment depending on the size of the file...")

try:
    with open(log_file, "r", errors="ignore") as f:
        # Read the entire file content at once
        content = f.read() 
        
        for match in pattern.finditer(content):
            raw_timestamp = match.group(1) 
            status = match.group(2)        
            user = match.group(3)          
            ip = match.group(4)            

            # Normalize spaces in the timestamp
            clean_timestamp = re.sub(r'\s+', ' ', raw_timestamp)
            
            # Format timestamp to YYYY-MM-DD HH:MM:SS
            try:
                date_obj = datetime.strptime(f"{current_year} {clean_timestamp}", "%Y %b %d %H:%M:%S")
                formatted_timestamp = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                formatted_timestamp = clean_timestamp # Fallback

            # Map to the specific events required by the project
            event = "failed_login" if status == "Failed" else "successful_login"

            data.append({
                "timestamp": formatted_timestamp,
                "user": user,
                "ip": ip,
                "event": event,
                "service": "sshd" 
            })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    if not df.empty:
        # Export to structured JSON [cite: 53]
        df.to_json(output_file, orient="records", indent=4)
        print(f"\nSuccess! Total parsed SSH events: {len(df)}")
        print(f"Data successfully exported to {output_file}")
        print("\nPreview of the parsed data:")
        print(df.head())
    else:
        print("\nNo matching SSH logs found. Please check your regex and file format.")

except FileNotFoundError:
    print(f"Error: '{log_file}' not found. Please ensure your log generator script finished running.")
