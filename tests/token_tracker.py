import json
import os
from datetime import datetime

LEDGER_FILE = os.path.join(os.path.dirname(__file__), "token_ledger.json")

# Simple pricing model (Approximate per 1M tokens)
PRICING = {
    "gemini-3.1-pro": {"input": 1.25, "output": 3.75},
    "gemini-3.1-flash": {"input": 0.03, "output": 0.12},
    "deepseek-v4-pro": {"input": 0.14, "output": 0.28},
    "deepseek-vl2": {"input": 0.10, "output": 0.20},
    "default": {"input": 0.50, "output": 1.50}
}

def log_usage(model, input_tokens, output_tokens, task_id="N/A"):
    """Logs token usage and updates the cumulative weight."""
    now = datetime.now().isoformat()
    
    # Load existing ledger
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            ledger = json.load(f)
    else:
        ledger = {"total_weight": 0, "total_cost": 0.0, "entries": []}

    # Calculate cost
    rates = PRICING.get(model, PRICING["default"])
    cost = (input_tokens / 1_000_000 * rates["input"]) + (output_tokens / 1_000_000 * rates["output"])
    
    # Update ledger
    entry = {
        "timestamp": now,
        "task_id": task_id,
        "model": model,
        "input": input_tokens,
        "output": output_tokens,
        "cost": round(cost, 6)
    }
    
    ledger["entries"].append(entry)
    ledger["total_weight"] += (input_tokens + output_tokens)
    ledger["total_cost"] = round(ledger["total_cost"] + cost, 4)
    
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)
    
    print(f"TOKEN WEIGHT UPDATED: Total Session Weight = {ledger['total_weight']} tokens | Total Cost = ${ledger['total_cost']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 3:
        log_usage(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else "N/A")
    else:
        # Just report current status
        if os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "r") as f:
                ledger = json.load(f)
            print(f"--- TOKEN WEIGHT REPORT ---")
            print(f"Total Tokens: {ledger['total_weight']}")
            print(f"Total Est. Cost: ${ledger['total_cost']}")
            print(f"Entries: {len(ledger['entries'])}")
        else:
            print("Token ledger is empty.")
