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

class HighVolumeActuator:
    def __init__(self):
        self.global_floor = datetime(2026, 5, 1)
        self.session_token = "SIM-VOLUME-STRESS-2026"
        self.intake_ids = []
        self.bin_ids = []
        self.egg_ids = []

    def log(self, phase, message):
        print(f"[{phase}] {message}")

    def call_rpc(self, rpc_name, payload):
        api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
        headers = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}
        payload_json = json.dumps(payload).replace("'", "''")
        query = f"SELECT public.{rpc_name}('{payload_json}'::jsonb);"
        return requests.post(api_url, headers=headers, json={"query": query})

    def execute_sql(self, sql):
        api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
        headers = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}
        return requests.post(api_url, headers=headers, json={"query": sql})

    def run_simulation(self):
        # 1. THE VOLUME SURGE (30 Intakes)
        self.log("VOLUME", "Executing Surge: 30 Intakes...")
        for i in range(30):
            staggered_date = self.global_floor + timedelta(days=i//2)
            species_id = (i % 5) + 1
            payload = {
                "species_id": species_id, "intake_date": staggered_date.strftime('%Y-%m-%d'),
                "session_id": self.session_token, "observer_id": 1,
                "intake": {"intake_name": f"WINC-2026-VOL-{100 + i}", "finder_turtle_name": f"Subject {i}"},
                "bins": [{"bin_code": f"B-{i}", "egg_count": 8, "bin_weight_g": 350.0}]
            }
            resp = self.call_rpc("vault_finalize_intake", payload)
            if resp.status_code == 200:
                res = resp.json()[0]['vault_finalize_intake']
                self.intake_ids.append(res['intake_id'])
                if i % 10 == 0: self.log("VOLUME", f"Processed {i} intakes...")
        
        # Collect IDs
        self.log("VOLUME", "Resolving Subject IDs...")
        bin_res = self.execute_sql("SELECT bin_id FROM bin").json()
        self.bin_ids = [b['bin_id'] for b in bin_res]
        egg_res = self.execute_sql("SELECT egg_id FROM egg").json()
        self.egg_ids = [e['egg_id'] for e in egg_res]

        # 2. THE OBSERVATION MATRIX (200+ Sessions)
        self.log("VOLUME", "Executing Observation Matrix: 200+ Sessions...")
        obs_queries = ["BEGIN;"]
        for j in range(200):
            bid = random.choice(self.bin_ids)
            eid = random.choice(self.egg_ids)
            staggered_obs = self.global_floor + timedelta(days=random.randint(15, 60))
            
            # Bin Observation
            obs_queries.append(f"""
                INSERT INTO public.bin_observation (session_id, bin_id, observer_id, observer_name, bin_weight_g, incubator_temp_f, humidity, env_notes)
                VALUES (1, {bid}, 1, 'Kevin Howland', {random.uniform(300,400)}, {random.uniform(82,85)}, {random.uniform(70,90)}, 'High-Volume Session {j}');
            """)
            
            # Egg Observation (Stage Saturation)
            stage = random.choice(['S1', 'S2', 'S3', 'S4', 'S5'])
            obs_queries.append(f"""
                INSERT INTO public.egg_observation (session_id, egg_id, bin_id, observer_id, stage_at_observation, observation_notes)
                VALUES (1, {eid}, {bid}, 1, '{stage}', 'Auto-property check stage {stage}');
            """)
            
            if len(obs_queries) > 50:
                obs_queries.append("COMMIT;")
                self.execute_sql("\n".join(obs_queries))
                obs_queries = ["BEGIN;"]
        
        if len(obs_queries) > 1:
            obs_queries.append("COMMIT;")
            self.execute_sql("\n".join(obs_queries))

        # 3. TERMINAL LIFECYCLE (Soft Deletes & Hatching)
        self.log("VOLUME", "Executing Terminal Transitions...")
        # Soft Deletes (10)
        self.execute_sql(f"UPDATE public.egg SET is_deleted = true WHERE egg_id IN ({','.join(map(str, self.egg_ids[:10]))});")
        # Mortality (10)
        self.execute_sql(f"UPDATE public.egg SET status = 'Dead' WHERE egg_id IN ({','.join(map(str, self.egg_ids[10:20]))});")
        # Hatching (20)
        for h_id in self.egg_ids[20:40]:
            self.execute_sql(f"INSERT INTO public.hatchling_ledger (egg_id, intake_id, session_id, hatch_weight_g, vitality_score) VALUES ({h_id}, 1, 1, 12.0, 'Strong');")
            self.execute_sql(f"UPDATE public.egg SET status = 'Transferred', current_stage = 'S6' WHERE egg_id = {h_id};")

        self.log("VOLUME", "Full Season Volume Simulation Complete.")

if __name__ == "__main__":
    HighVolumeActuator().run_simulation()
