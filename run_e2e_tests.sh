#!/bin/bash

# End-to-End Testing Script for Resilience App
# Starts backend, runs tests, captures results

set -e

echo "🚀 Starting End-to-End Test Suite"

# Check if backend is running
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "⚠️  Backend not running. Starting backend..."
    cd resilience-backend
    python -m uvicorn app.main:app --reload &
    BACKEND_PID=$!
    echo "🔄 Waiting for backend to start..."
    sleep 5
    cd ..
else
    echo "✅ Backend already running"
    BACKEND_PID=""
fi

# Run E2E tests
echo "🧪 Running End-to-End Tests..."
cd resilience-backend
python test_e2e.py

# Store exit code
TEST_EXIT_CODE=$?

# Cleanup
if [ ! -z "$BACKEND_PID" ]; then
    echo "🧹 Stopping backend..."
    kill $BACKEND_PID 2>/dev/null || true
fi

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All E2E tests passed!"
else
    echo "💥 E2E tests failed!"
fi

exit $TEST_EXIT_CODE