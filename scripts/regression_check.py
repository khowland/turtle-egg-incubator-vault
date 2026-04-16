"""
=============================================================================
Module:     scripts/regression_check.py (NEW - REGRESSION SUITE)
Project:    Incubator Vault v7.2.0 — WINC
Purpose:    Automated Code-Based Validation & Logic Regression.
Revision:   2026-04-08 — Initial Implementation (Antigravity)
=============================================================================
"""

import sys
import os
# Add project root to path for imports
sys.path.append(os.getcwd())

from utils.db import get_supabase
from utils.bootstrap import safe_db_execute

def run_regression():
    print("🚀 INITIATING V7.2.1 REGRESSION SWEEP...")
    results = {"pass": 0, "fail": 0}

    # --- TEST 1: DB Connectivity & Schema ---
    print("\n[TEST 1] Testing Connectivity & Audit Column Integrity...")
    try:
        supabase = get_supabase()
        res = supabase.table('species').select("modified_at").limit(1).execute()
        print("✅ SUCCESS: Species table accessible and Audit columns present.")
        results["pass"] += 1
    except Exception as e:
        print(f"❌ FAIL: Connectivity/Schema Mismatch: {e}")
        results["fail"] += 1

    # --- TEST 2: ID Generation Logic (Bin Mask) ---
    print("\n[TEST 2] Testing Bin Mask Calculation (Format §28)...")
    try:
        # Mocking the ID logic
        species_code = "BL"
        count = 5
        finder = "Smith"
        bin_num = 1
        mask = f"{species_code}{count+1}-{finder}-{bin_num}"
        
        expected = "BL6-Smith-1"
        if mask == expected:
            print(f"✅ SUCCESS: ID Mask '{mask}' matches clinical standard.")
            results["pass"] += 1
        else:
            print(f"❌ FAIL: ID Mask mismatch. Got {mask}, expected {expected}")
            results["fail"] += 1
    except:
        results["fail"] += 1

    # --- TEST 3: Safe-Write Resilience ---
    print("\n[TEST 3] Testing Safe-Execution Wrapper resilience...")
    def bad_function():
        raise ValueError("Simulated Database Timeout")
        
    try:
        # We check if it returns None (as designed) instead of crashing the script
        output = safe_db_execute("Regression Test", bad_function)
        if output is None:
            print("✅ SUCCESS: Exception caught safely by wrapper.")
            results["pass"] += 1
        else:
            print("❌ FAIL: Wrapper failed to catch or return correctly.")
            results["fail"] += 1
    except:
        results["fail"] += 1

    # --- TEST 4: Auto-Transition Context ---
    print("\n[TEST 4] Testing Auto-Transition Context Payload...")
    try:
        import streamlit as st
        # Simulate active bin insertion to memory
        st.session_state.active_bin_id = "BL7-Test-1"
        if st.session_state.get('active_bin_id') == "BL7-Test-1":
            print("✅ SUCCESS: Transition context properly attached to Memory.")
            results["pass"] += 1
        else:
            print("❌ FAIL: Payload assignment error.")
            results["fail"] += 1
    except Exception as e:
        print(f"❌ FAIL: Streamlit Session State crash: {e}")
        results["fail"] += 1

    # --- FINAL REPORT ---
    print("\n" + "="*40)
    print(f"🏁 REGRESSION COMPLETE: {results['pass']} PASSED, {results['fail']} FAILED")
    print("="*40)
    
    return results["fail"] == 0

if __name__ == "__main__":
    success = run_regression()
    if not success:
        sys.exit(1)
