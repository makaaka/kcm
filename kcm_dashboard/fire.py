import requests
import json
from datetime import datetime

# Firebase Realtime Database URL (your project)
DATABASE_URL = "https://kcm-e-f27f0-default-rtdb.firebaseio.com"

# Data to send
data = {
    "value": 42,
    "temperature": 25.6,
    "status": "OK",
    "timestamp": datetime.now().isoformat()
}

# Path to write to
firebase_path = "/test.json"  # The ".json" is required for Firebase REST API

# Send data using HTTP PUT or PATCH (PUT replaces, PATCH updates)
response = requests.patch(DATABASE_URL + firebase_path, json=data)

# Check result
if response.status_code == 200:
    print("✅ Data sent successfully:")
    print(response.json())
else:
    print("❌ Failed to send data:")
    print(response.status_code, response.text)
