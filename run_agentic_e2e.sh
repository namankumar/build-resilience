#!/bin/bash

# Agentic End-to-End Testing Script
# Uses AI agents to intelligently test user workflows

set -e

echo "🤖 Starting Agentic End-to-End Testing"

# Check dependencies
echo "🔍 Checking dependencies..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q playwright openai asyncio

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create screenshots directory
mkdir -p test_screenshots

# Run agentic E2E tests
echo "🧪 Running Agentic E2E Tests..."
python test_agentic_e2e.py

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All agentic E2E tests passed!"
    echo "📸 Screenshots saved in test_screenshots/"
else
    echo "💥 Agentic E2E tests failed!"
fi

exit $TEST_EXIT_CODE