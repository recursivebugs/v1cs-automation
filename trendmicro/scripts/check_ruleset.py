#!/usr/bin/env python3
import requests
import json
import yaml
import os
import sys
import traceback


def load_ruleset_file(ruleset_file_path):
    try:
        with open(ruleset_file_path, 'r') as file:
            if ruleset_file_path.endswith(('.yaml', '.yml')):
                print("Detected YAML format")
                return yaml.safe_load(file)
            elif ruleset_file_path.endswith('.json'):
                print("Detected JSON format")
                return json.load(file)
            else:
                print("Unsupported ruleset file format. Please use .yaml, .yml, or .json")
                sys.exit(1)
    except Exception as e:
        print(f"Error reading ruleset file: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


def create_ruleset():
    try:
        API_KEY = os.environ.get('API_KEY')
        RULESET_FILE = os.environ.get('RULESET_FILE')
        RULESET_NAME = os.environ.get('RULESET_NAME', 'Default Ruleset')

        if not API_KEY or not RULESET_FILE:
            print("Missing required environment variables: API_KEY, RULESET_FILE")
            sys.exit(1)

        print(f"Reading ruleset file: {RULESET_FILE}")

        if not os.path.isfile(RULESET_FILE):
            print(f"Error: File not found at {RULESET_FILE}")
            sys.exit(1)

        ruleset_data = load_ruleset_file(RULESET_FILE)

        rules = []

        if isinstance(ruleset_data, dict) and 'rules' in ruleset_data:
            rules_data = ruleset_data['rules']
            for rule in rules_data:
                rule_obj = {
                    "id": rule.get('type', ''),
                    "action": rule.get('action', 'log')
                }
                if 'properties' in rule:
                    rule_obj['properties'] = rule['properties']
                if 'namespaces' in rule:
                    rule_obj['namespaces'] = rule['namespaces']
                rules.append(rule_obj)

        elif isinstance(ruleset_data, dict) and 'apiVersion' in ruleset_data:
            spec = ruleset_data.get('spec', {})
            definition = spec.get('definition', {})
            rules_data = definition.get('rules', [])
            for rule in rules_data:
                rule_obj = {
                    "id": rule.get('ruleID', ''),
                    "action": rule.get('mitigation', rule.get('action', 'log'))
                }
                rules.append(rule_obj)

        api_data = {
            "name": RULESET_NAME,
            "description": f"Created from {RULESET_FILE}",
            "rules": rules
        }

        print(f"Prepared API request payload with {len(rules)} rules:")
        print(json.dumps(api_data, indent=2))

        url = "https://api.xdr.trendmicro.com/beta/containerSecurity/rulesets"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'api-version': 'v1',
            'Authorization': f'Bearer {API_KEY}'
        }

        print("Sending request to API...")
        response = requests.post(url, headers=headers, json=api_data)

        print(f"API Response Status: {response.status_code}")
        print(f"API Response Body: {response.text}")

        if response.status_code in [200, 201]:
            result = response.json()
            ruleset_id = result.get('id', 'CREATED_BUT_ID_UNKNOWN')
            print(f"Ruleset created successfully with ID: {ruleset_id}")
            print(f"ruleset_id={ruleset_id}")
        else:
            print(f"Error creating ruleset: HTTP {response.status_code}")
            sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_ruleset()
