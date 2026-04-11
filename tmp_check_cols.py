from utils.db import get_supabase
import json

def check_cols():
    supabase = get_supabase()
    res = supabase.table('incubatorobservation').select('*').limit(1).execute()
    print(json.dumps(res.data, indent=2))

if __name__ == "__main__":
    check_cols()
