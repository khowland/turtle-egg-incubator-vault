from utils.db import get_supabase
import json

def discover():
    sb = get_supabase()
    tables = ['incubatorobservation', 'binobservation', 'bin_observation', 'incubator_observation']
    for t in tables:
        try:
            res = sb.table(t).select('*').limit(1).execute()
            print(f"Table '{t}' exists. Rows: {len(res.data)}")
            if len(res.data) > 0:
                print(f"Columns in '{t}': {list(res.data[0].keys())}")
            else:
                # Try to get columns by inserting a dummy
                print(f"Table '{t}' is empty.")
        except Exception as e:
            print(f"Table '{t}' access failed: {e}")

if __name__ == "__main__":
    discover()
