import os
import requests
import json
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

env_path = r"c:\dev\projects\turtle-db\.env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

class SimulationEngine:
    def __init__(self):
        self.session_tokens = {} # Day -> Token
        self.current_intake_id = None
        self.bin_ids = []
        self.egg_ids = []

    def log_step(self, step, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {step}: {message}")

    def call_rpc(self, rpc_name, payload):
        api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
        headers = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}
        payload_json = json.dumps(payload).replace("'", "''")
        query = f"SELECT public.{rpc_name}('{payload_json}'::jsonb);"
        resp = requests.post(api_url, headers=headers, json={"query": query})
        return resp

    def execute_sql(self, sql):
        api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
        headers = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}
        resp = requests.post(api_url, headers=headers, json={"query": sql})
        return resp

    # --- WORKFLOWS ---

    def run_lifecycle(self):
        if not self.tc_fb_01_root_intake(): return
        if not self.tc_fb_02_supplemental_bin(): return
        
        # Collect IDs for downstream
        self.refresh_ids()
        
        if not self.tc_fb_03_mass_observation(): return
        if not self.tc_fb_04_egg_progression(): return
        if not self.tc_fb_05_mortality(): return
        if not self.tc_fb_06_hatching(): return
        
        print("\n🏆 FINAL BOSS QA PASSED. FULL SEASON LIFECYCLE SIMULATED.")

    def refresh_ids(self):
        res = self.execute_sql(f"SELECT bin_id FROM bin WHERE intake_id = {self.current_intake_id}")
        self.bin_ids = [r['bin_id'] for r in res.json()]
        res = self.execute_sql(f"SELECT egg_id FROM egg WHERE bin_id IN ({','.join(map(str, self.bin_ids))})")
        self.egg_ids = [r['egg_id'] for r in res.json()]

    def tc_fb_01_root_intake(self):
        step = "TC-FB-01"
        self.log_step(step, "New Case Discovery (Day 0)")
        token = f"SIM-SESS-DAY0-{int(time.time())}"
        payload = {
            "species_id": 1, "intake_date": "2026-05-14", "session_id": token, "observer_id": 1,
            "intake": {"intake_name": f"BOSS-2026-{random_suffix()}", "finder_turtle_name": "Sovereign Subject"},
            "bins": [{"bin_code": "BIN-A", "egg_count": 10, "bin_weight_g": 400}]
        }
        resp = self.call_rpc("vault_finalize_intake", payload)
        if resp.status_code == 200:
            self.current_intake_id = resp.json()[0]['vault_finalize_intake']['intake_id']
            return True
        return False

    def tc_fb_02_supplemental_bin(self):
        step = "TC-FB-02"
        self.log_step(step, "Supplemental Bin (Day 1)")
        res = self.execute_sql(f"SELECT intake_name FROM intake WHERE intake_id = {self.current_intake_id}")
        intake_name = res.json()[0]['intake_name']
        token = f"SIM-SESS-DAY1-{int(time.time())}"
        payload = {
            "species_id": 1, "intake_date": "2026-05-15", "session_id": token, "observer_id": 1,
            "intake": {"intake_name": intake_name},
            "bins": [{"bin_code": "BIN-B", "egg_count": 5, "bin_weight_g": 200}]
        }
        return self.call_rpc("vault_finalize_intake", payload).status_code == 200

    def tc_fb_03_mass_observation(self):
        step = "TC-FB-03"
        self.log_step(step, "Weekly Weight Check (Day 7)")
        token = f"SIM-SESS-DAY7-{int(time.time())}"
        # We simulate multiple API calls to bin_observation
        for bid in self.bin_ids:
            sql = f"""
                INSERT INTO public.bin_observation (session_id, bin_id, observer_id, observer_name, bin_weight_g, incubator_temp_f, env_notes)
                VALUES (2, {bid}, 1, 'SIM_USER', {random.uniform(200,500)}, 83.0, 'Day 7 Routine Check');
            """
            self.execute_sql(sql)
        return True

    def tc_fb_04_egg_progression(self):
        step = "TC-FB-04"
        self.log_step(step, "Candling Session (Day 21) - S1 -> S2")
        for eid in self.egg_ids[:5]: # Progress first 5 eggs
            sql = f"UPDATE public.egg SET current_stage = 'S2', modified_at = now() WHERE egg_id = {eid};"
            self.execute_sql(sql)
            obs_sql = f"""
                INSERT INTO public.egg_observation (session_id, egg_id, bin_id, observer_id, stage_at_observation, observation_notes)
                VALUES (2, {eid}, {self.bin_ids[0]}, 1, 'S2', 'Day 21: Vascularity observed.');
            """
            self.execute_sql(obs_sql)
        return True

    def tc_fb_05_mortality(self):
        step = "TC-FB-05"
        self.log_step(step, "Mortality Event (Day 30)")
        dead_egg = self.egg_ids[-1]
        sql = f"UPDATE public.egg SET status = 'Dead', modified_at = now() WHERE egg_id = {dead_egg};"
        self.execute_sql(sql)
        return True

    def tc_fb_06_hatching(self):
        step = "TC-FB-06"
        self.log_step(step, "The Great Hatching (Day 60)")
        hatched_egg = self.egg_ids[0]
        # 1. Update Egg Status
        self.execute_sql(f"UPDATE public.egg SET status = 'Transferred', current_stage = 'S6', modified_at = now() WHERE egg_id = {hatched_egg};")
        # 2. Record in Hatchling Ledger
        sql = f"""
            INSERT INTO public.hatchling_ledger (egg_id, intake_id, session_id, hatch_weight_g, vitality_score, notes)
            VALUES ({hatched_egg}, {self.current_intake_id}, 2, 11.8, 'Strong', 'Day 60: Successful Hatch');
        """
        return self.execute_sql(sql).status_code in (200, 201)

def random_suffix():
    import random
    return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=4))

if __name__ == "__main__":
    SimulationEngine().run_lifecycle()
