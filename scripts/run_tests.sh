#!/usr/bin/env bash
#
# run_tests.sh
#
# Orchestrates the full test run: sets up a virtual environment if needed,
# installs dependencies, runs the automated suite, and prints a pass/fail
# summary along with an HTML report. Meant to be runnable locally or in CI.
#
# Usage:
#   ./scripts/run_tests.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

VENV_DIR=".venv"
REPORT_DIR="reports"

echo "== Backend Test Automation :: run started at $(date) =="

# 1. Set up virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "-> Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "-> Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 2. Prepare report output directory
mkdir -p "$REPORT_DIR"

# 3. Run the automated suite
echo "-> Running pytest suite..."
set +e
pytest -v \
    --junitxml="$REPORT_DIR/junit.xml" \
    --html="$REPORT_DIR/report.html" --self-contained-html \
    tests/
TEST_EXIT_CODE=$?
set -e

# 4. Summarize results
echo ""
echo "== Summary =="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "RESULT: PASS - all tests green"
else
    echo "RESULT: FAIL - see $REPORT_DIR/report.html for details"
fi

echo "JUnit XML: $REPORT_DIR/junit.xml"
echo "HTML report: $REPORT_DIR/report.html"
echo "== Run finished at $(date) =="

exit $TEST_EXIT_CODE
