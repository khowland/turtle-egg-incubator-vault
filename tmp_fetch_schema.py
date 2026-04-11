import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
url = os.getenv("SUPABASE_URL") + "/rest/v1/"
headers = {"apikey": os.getenv("SUPABASE_SERVICE_ROLE_KEY")}

def fetch_openapi():
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            spec = r.json()
            # print(json.dumps(spec, indent=2))
            # We specifically look for incubatorobservation columns
            tables = spec.get('definitions', {})
            if 'incubatorobservation' in tables:
                print("Columns in 'incubatorobservation':")
                cols = tables['incubatorobservation'].get('properties', {})
                for col in cols:
                    print(f"  - {col}")
            else:
                print("Table 'incubatorobservation' not found in OpenAPI definitions.")
                # Maybe it's under a different name?
                print("Available definitions:", list(tables.keys()))
        else:
            print(f"Failed to fetch OpenAPI spec: {r.status_code}")
            print(r.text)
    except Exception as e:
        print(f"Error fetching OpenAPI: {e}")

if __name__ == "__main__":
    fetch_openapi()
