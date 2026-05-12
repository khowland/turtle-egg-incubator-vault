#!/usr/bin/env python3
"""scripts/trace_extract.py — extract full request timeline by trace_id."""
import sys, os, glob

def main():
    if len(sys.argv) != 2:
        print("Usage: trace_extract.py <trace_id>")
        sys.exit(1)
    tid = sys.argv[1]
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs = glob.glob(os.path.join(base, 'logs', '*.log'))
    for lf in sorted(logs):
        with open(lf) as f:
            lines = [line for line in f if tid in line]
            if lines:
                print(f"--- {os.path.basename(lf)} ---")
                for line in lines:
                    print(line.rstrip())
                print()

if __name__ == '__main__':
    main()
