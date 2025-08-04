import requests
from requests.auth import HTTPBasicAuth

with open("responses.json", "r", encoding="utf-8") as f:
    data = f.read()

response = requests.post(
    "https://localhost/_config",
    headers={"Content-Type": "application/json"},
    data=data,
    auth=HTTPBasicAuth("admin", "dust514"),
    verify=False  # self-signed cert
)

print(response.status_code, response.text)
