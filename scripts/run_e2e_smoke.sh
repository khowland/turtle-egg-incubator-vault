#!/bin/bash
set -euo pipefail
python3 scripts/e2e_launcher.py --suite smoke --startup-timeout 60 --test-timeout 240
