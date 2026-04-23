import json
import pandas as pd
from pathlib import Path
import sys

def analyze_performance(file_path):
    if not Path(file_path).exists():
        print(f"Error: {file_path} not found.")
        return

    data = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not data:
        print("No telemetry data found.")
        return

    df = pd.DataFrame(data)
    
    # Filter for SUCCESS only for latency stats
    success_df = df[df['status'] == 'SUCCESS']
    
    if success_df.empty:
        print("No successful view traces found.")
    else:
        stats = success_df.groupby('view')['duration_s'].agg(['count', 'mean', 'min', 'max', 'std']).round(3)
        print("\n=== UI View Latency Statistics (Seconds) ===")
        print(stats)

    # Errors
    error_df = df[df['status'] == 'ERROR']
    if not error_df.empty:
        print("\n=== View Errors Found ===")
        print(error_df[['timestamp', 'view']])

    # Splash Screen Check
    splash_df = success_df[success_df['view'] == 'Login/Splash']
    if not splash_df.empty:
        avg_splash = splash_df['duration_s'].mean()
        print(f"\nAverage Splash Screen Load: {avg_splash:.3f}s")
        if avg_splash < 1.0:
            print("✅ PASSED: Splash screen below 1.0s threshold.")
        else:
            print("❌ FAILED: Splash screen exceeds 1.0s threshold.")
    else:
        print("\n⚠️ WARNING: No 'Splash' screen telemetry found.")

if __name__ == "__main__":
    analyze_performance("reports/performance_telemetry.jsonl")
