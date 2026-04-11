from utils.db import get_supabase
import uuid

def insert_dummy():
    sb = get_supabase()
    try:
        # Try to insert a row with just a random obs_id and bin_id
        # We use a non-existent bin_id to avoid FK issues if possible, or just a valid one
        res = sb.table('incubatorobservation').insert({"obs_id": str(uuid.uuid4()), "bin_id": "NON_EXISTENT_BIN"}).execute()
        print("Insert succeeded! Columns in table:")
        print(list(res.data[0].keys()))
    except Exception as e:
        print(f"Insert failed: {e}")

if __name__ == "__main__":
    insert_dummy()
