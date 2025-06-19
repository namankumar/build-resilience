#!/bin/bash

# Full End-to-End Testing Script
# Tests both React Native frontend and Python backend together

set -e

echo "🚀 Starting Full End-to-End Test Suite (Frontend + Backend)"

# Check dependencies
echo "🔍 Checking dependencies..."

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js"
    exit 1
fi

# Check if python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python not found"
    exit 1
fi

# Check if ChromeDriver is available
if ! command -v chromedriver &> /dev/null; then
    echo "⚠️  ChromeDriver not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install chromedriver
    else
        echo "❌ Please install ChromeDriver manually"
        echo "   Visit: https://chromedriver.chromium.org/"
        exit 1
    fi
fi

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
cd resilience-backend
if [ ! -d "venv" ]; then
    python -m venv venv
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true

pip install -q selenium requests
cd ..

# Install frontend dependencies if needed
echo "📦 Installing frontend dependencies..."
cd ResilienceApp
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Run the full E2E tests
echo "🧪 Running Full End-to-End Tests..."
python test_full_e2e.py

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All Full E2E tests passed!"
else
    echo "💥 Full E2E tests failed!"
fi

exit $TEST_EXIT_CODE