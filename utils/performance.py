"""
=============================================================================
Module:        utils/performance.py
Project:       Incubator Vault v8.1.4
Purpose:       UI Latency Instrumentation & Telemetry.
Requirement:   Phase 4 Performance Audit Standard.
=============================================================================
"""
import time
import streamlit as st
from utils.logger import logger
import json
import os

TELEMETRY_PATH = "reports/performance_telemetry.jsonl"

class ViewTimer:
    """
    Context manager to measure the execution time of a Streamlit view.
    Automatically logs results to a telemetry file.
    """
    def __init__(self, view_name):
        self.view_name = view_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        
        telemetry_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "view": self.view_name,
            "duration_s": round(duration, 4),
            "status": "SUCCESS" if exc_type is None else "ERROR",
            "session_id": st.session_state.get("session_id", "UNKNOWN")
        }

        # Log to system logger
        logger.info(f"⏱️ Performance: {self.view_name} loaded in {duration:.4f}s")
        
        # Save to local telemetry file
        try:
            os.makedirs(os.path.dirname(TELEMETRY_PATH), exist_ok=True)
            with open(TELEMETRY_PATH, "a") as f:
                f.write(json.dumps(telemetry_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write telemetry: {e}")

def track_view_performance(view_name):
    """
    Helper to wrap a view's execution in a timer.
    Usage:
        with track_view_performance("Dashboard"):
            # view logic here
    """
    return ViewTimer(view_name)
