#!/bin/bash

# OTA Monitor Test Runner Script
# This script sets up the environment and runs the pytest suite with coverage.

echo "🚀 Starting OTA Monitor Test Suite..."

# Set PYTHONPATH to include the current directory so ota_monitor is discoverable
export PYTHONPATH=$PYTHONPATH:.

# Run pytest with coverage and terminal reporting
pytest --cov=ota_monitor tests/ -v

# Capture the exit code of pytest
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Tests passed successfully!"
else
    echo "❌ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
