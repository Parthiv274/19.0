import requests
import sys

BASE_URL = "http://localhost:8045"
DATABASE = "partner_credit_limit_v19_1"
USERNAME = "admin"
PASSWORD = "admin"

session = requests.Session()
headers = {
    "Content-Type": "application/json",
    "User-Agent": "partner_credit_script"
}

login_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": DATABASE,
        "login": USERNAME,
        "password": PASSWORD
    },
    "id": 1
}

login_response = session.post(f"{BASE_URL}/web/session/authenticate", headers=headers, json=login_payload)
login_result = login_response.json()

if not login_result.get("result"):
    print("Login failed")
    sys.exit()

print("Login successful")

search_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "res.partner",
        "method": "search_read",
        "args": [],
        "kwargs": {
            "fields": ["name", "credit_limit"],
            "context": {"lang": "en_US"}
        }
    },
    # "id": 2
}

search_response = session.post(f"{BASE_URL}/web/dataset/call_kw", headers=headers, json=search_payload)
partners = search_response.json().get("result", [])

print(f"\nFound {len(partners)} partners:\n")

for partner in partners:
    name = partner.get('name', 'N/A')
    credit_limit = partner.get('credit_limit', 0)
    print(f"Name: {name}, Credit Limit: {credit_limit}")