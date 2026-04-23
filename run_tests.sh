#!/usr/bin/env bash
# =============================================================================
# run_tests.sh — Reliable Test Runner for TurtleDB
# =============================================================================
# PURPOSE: Ensures pytest and all test dependencies are always available
#          before running the suite. Solves the recurring "pytest disappeared"
#          problem caused by running tests inside the Agent Zero container
#          (/opt/venv) which resets between sessions.
#
# USAGE:
#   ./run_tests.sh               # Run all unit tests (excludes e2e/playwright)
#   ./run_tests.sh --all         # Include e2e playwright tests
#   ./run_tests.sh tests/test_vault_logic.py  # Run a specific file
#
# WHY THIS EXISTS:
#   The project .venv is a Windows virtual environment (.venv/Scripts/pytest.exe)
#   and does not run on Linux. When tests are run from the Agent Zero Linux
#   container (/opt/venv), pytest must be installed into that environment.
#   requirements.txt already lists pytest>=9.0.0 but the container /opt/venv
#   is not rebuilt from requirements.txt automatically.
# =============================================================================

set -e

PYTHON="$(which python3 || which python)"
PIP="$PYTHON -m pip"

echo "🐍 Python: $PYTHON"
echo "📦 Checking test dependencies..."

# Install from requirements.txt into active environment (quiet, fast if cached)
$PIP install -q pytest pytest-mock plotly streamlit supabase python-dotenv pandas

echo "✅ Dependencies ready"
echo ""

# Determine test scope
if [[ "$1" == "--all" ]]; then
    echo "🧪 Running ALL tests (including e2e)..."
    $PYTHON -m pytest tests/ -v --tb=short "${@:2}"
elif [[ -n "$1" ]]; then
    echo "🧪 Running: $1"
    $PYTHON -m pytest "$1" -v --tb=short "${@:2}"
else
    echo "🧪 Running unit tests (excluding e2e/playwright)..."
    $PYTHON -m pytest tests/ -v --tb=short \
        --ignore=tests/e2e_playwright \
        --ignore=tests/clinical_edge_cases
fi
