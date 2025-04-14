import requests
import sys
import os
import json

api_key = os.getenv("API_KEY")
ruleset_id = os.getenv("RULESET_ID")
policy_path = "trendmicro/policy.json"

url = "https://api.xdr.trendmicro.com/beta/containerSecurity/policies"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

try:
    with open(policy_path) as f:
        policy = json.load(f)

    if "rulesets" in policy:
        policy["rulesets"][0]["id"] = ruleset_id
    else:
        policy["rulesets"] = [{"id": ruleset_id}]

    res = requests.post(url, headers=headers, json=policy)
    if res.status_code == 201:
        print("Policy created successfully.")
        sys.exit(0)
    else:
        print(f"[ERROR] Failed to create policy: {res.status_code} {res.text}")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Failed to create policy: {e}")
    sys.exit(1)
