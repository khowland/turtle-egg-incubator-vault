#!/bin/bash
set -euo pipefail
python3 scripts/e2e_launcher.py --suite full --startup-timeout 60 --test-timeout 480
