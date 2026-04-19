from streamlit.testing.v1 import AppTest
import time
import json
from pathlib import Path

def run_headless_audit():
    print("🚀 STARTING HEADLESS UI PERFORMANCE AUDIT (AppTest)...")
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    # 1. Login Simulation
    print("Logging in as Kevin...")
    # Find the selectbox for observer
    at.selectbox[0].select("Kevin Howland").run()
    # Find the pin input
    at.text_input[0].set_value("1234").run()
    # Click START
    at.button[0].click().run()

    if at.error:
        print(f"❌ Login failed: {at.error}")
        return

    print("✅ Logged in. Navigating views...")

    # 2. Sequential Navigation
    # Note: st.navigation pages can be switched via switch_page if we are in the script,
    # but AppTest simulates the user. We need to find the navigation widgets.
    # However, AppTest.from_file("app.py") will run app.py which renders the sidebar.
    
    views = [
        "vault_views/1_Dashboard.py",
        "vault_views/2_New_Intake.py",
        "vault_views/3_Observations.py",
        "vault_views/5_Settings.py",
        "vault_views/6_Reports.py",
        "vault_views/7_Diagnostic.py",
        "vault_views/8_Help.py"
    ]

    for view in views:
        print(f"Switching to {view}...")
        # In AppTest, we can simulate switch_page by setting the internal state or clicking nav
        # For simplicity in this audit, we'll try to trigger the rerun for each file
        at.switch_page(view).run()
        if at.error:
            print(f"❌ Error in {view}: {at.error}")
        else:
            print(f"✅ {view} responsive.")
        time.sleep(0.5)

    print("\n=== Audit Simulation Complete ===")
    print("Check reports/performance_telemetry.jsonl for latency data.")

if __name__ == "__main__":
    run_headless_audit()
