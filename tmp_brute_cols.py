from utils.db import get_supabase

def brute():
    sb = get_supabase()
    cols = ['bin_weight_g', 'bin_weight', 'weight_g', 'weight', 'mass_g', 'bin_mass', 'total_weight', 'bin_weight_grams']
    for c in cols:
        try:
            sb.table('incubatorobservation').select(c).limit(1).execute()
            print(f"✅ Success! Column is '{c}'")
            return
        except Exception as e:
            if 'does not exist' not in str(e):
                # If it's 200/206 but empty, it won't throw 'does not exist'
                print(f"🤔 Column '{c}' might exist but returned: {e}")
            else:
                pass
    print("❌ Failed to find weight column.")

if __name__ == "__main__":
    brute()
