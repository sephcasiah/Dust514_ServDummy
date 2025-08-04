import requests
from requests.auth import HTTPBasicAuth
import json

BASE_URL = "http://127.0.0.1:8000"
AUTH = HTTPBasicAuth('admin', 'dust514')

# 🧪 1. Test ping without config
print("[Test] GET /ping...")
r = requests.get(f"{BASE_URL}/ping")
print(r.status_code, r.text)
print("\n")

# 🧪 2. Post valid config
print("[Test] POST /_config...")
config = {
    "/ping": {
        "GET": [
            {
                "status": 200,
                "response": {
                    "message": "pong!"
                }
            }
        ]
    }
}
r = requests.post(f"{BASE_URL}/_config", auth=AUTH, json=config)
print(r.status_code, r.text)
print("\n")

# 🧪 3. Ping again with config loaded
print("[Test] GET /ping...")
r = requests.get(f"{BASE_URL}/ping")
print(r.status_code, r.text)
print("\n")

# 🧪 4. Post invalid config
print("[Test] POST /_config (invalid)...")
bad_config = "{ this is not valid json"
r = requests.post(f"{BASE_URL}/_config", auth=AUTH, data=bad_config, headers={"Content-Type": "application/json"})
print(r.status_code, r.text)
print("\n")

# 🧪 5. Try shutdown
print("[Test] POST /_shutdown...")
r = requests.post(f"{BASE_URL}/_shutdown", auth=AUTH)
print(r.status_code, r.text)
