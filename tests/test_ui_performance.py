import os
import time
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st

# Mock streamlit to avoid issues in non-interactive environment
if not hasattr(st, "cache_data"):
    st.cache_data = lambda **kwargs: lambda f: f

from utils.session import fetch_active_observers

def test_fetch_active_observers_performance():
    # Warm up cache
    start_time = time.time()
    fetch_active_observers()
    first_run_duration = time.time() - start_time
    
    # Second run (should be cached)
    start_time = time.time()
    fetch_active_observers()
    second_run_duration = time.time() - start_time
    
    print(f"\nFirst run duration: {first_run_duration:.4f}s")
    print(f"Second run duration: {second_run_duration:.4f}s")
    
    # Second run should be significantly faster
    assert second_run_duration < first_run_duration
    assert second_run_duration < 0.01  # Cached lookup should be sub-millisecond essentially

if __name__ == "__main__":
    test_fetch_active_observers_performance()
