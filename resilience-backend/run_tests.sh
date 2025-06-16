#!/bin/bash

# Resilience App Backend Test Runner
# This script starts the server, runs tests, and logs results

set -e  # Exit on any error

# Configuration
SERVER_HOST="127.0.0.1"
SERVER_PORT="8001"
LOG_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"
PID_FILE="server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to cleanup server
cleanup() {
    log "${YELLOW}🧹 Cleaning up...${NC}"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            log "   Stopping server (PID: $PID)"
            kill "$PID" 2>/dev/null || true
            sleep 2
            # Force kill if still running
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any remaining uvicorn processes on our port
    lsof -ti:$SERVER_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    
    log "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Start the script
log "${BLUE}🚀 Starting Resilience App Backend Test Suite${NC}"
log "   Time: $(date)"
log "   Log file: $LOG_FILE"
log "   Server: http://$SERVER_HOST:$SERVER_PORT"
log "$(echo '='| tr ' ' '=')$(printf '=%.0s' {1..60})"

# Activate virtual environment
log "${YELLOW}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies if needed
log "${YELLOW}📦 Checking dependencies...${NC}"
pip install -q requests 2>/dev/null || log "   Dependencies already installed"

# Kill any existing processes on the port
log "${YELLOW}🔄 Checking for existing processes on port $SERVER_PORT...${NC}"
lsof -ti:$SERVER_PORT 2>/dev/null | xargs kill -9 2>/dev/null || log "   No existing processes found"

# Start the server
log "${YELLOW}🏁 Starting test server...${NC}"
python -m uvicorn test_server:app --host $SERVER_HOST --port $SERVER_PORT 2>&1 | tee -a "$LOG_FILE" &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

log "   Started server with PID: $SERVER_PID"

# Wait for server to be ready
log "${YELLOW}⏳ Waiting for server to be ready...${NC}"
MAX_ATTEMPTS=15
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://$SERVER_HOST:$SERVER_PORT/health > /dev/null 2>&1; then
        log "${GREEN}✅ Server is ready!${NC}"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    log "   Attempt $ATTEMPT/$MAX_ATTEMPTS - Server not ready yet..."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    log "${RED}❌ Server failed to start after $MAX_ATTEMPTS attempts${NC}"
    exit 1
fi

# Run the tests
log "\n${BLUE}🧪 Running API tests...${NC}"
python test_api.py 2>&1 | tee -a "$LOG_FILE"

# Check test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log "\n${GREEN}🎉 All tests completed successfully!${NC}"
    EXIT_CODE=0
else
    log "\n${RED}❌ Some tests failed${NC}"
    EXIT_CODE=1
fi

# Server logs
log "\n${BLUE}📋 Final server status:${NC}"
if kill -0 "$SERVER_PID" 2>/dev/null; then
    log "   Server is still running (PID: $SERVER_PID)"
else
    log "   Server has stopped"
fi

# Summary
log "\n${BLUE}📊 Test Summary:${NC}"
log "   Log file: $LOG_FILE"
log "   Server: http://$SERVER_HOST:$SERVER_PORT"
log "   Exit code: $EXIT_CODE"

# Don't exit with error code so cleanup runs
exit $EXIT_CODE