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
            definitions = spec.get('definitions', {})
            for table_name in definitions:
                print(f"\n--- Table: {table_name} ---")
                cols = definitions[table_name].get('properties', {})
                for col in cols:
                    print(f"  - {col}")
        else:
            print(f"Failed to fetch OpenAPI spec: {r.status_code}")
    except Exception as e:
        print(f"Error fetching OpenAPI: {e}")

if __name__ == "__main__":
    fetch_openapi()
