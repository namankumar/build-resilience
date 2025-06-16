#!/bin/bash

# 🌟 Resilience App - One-Click Startup Script
# This script starts both backend and frontend for full experience

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="/Users/namankumar/Downloads/github/claude-project"
BACKEND_DIR="$PROJECT_ROOT/resilience-backend"
FRONTEND_DIR="$PROJECT_ROOT/ResilienceApp"

echo -e "${PURPLE}🌟 Starting Resilience App - Complete Experience${NC}"
echo -e "${BLUE}=================================================${NC}"

# Function to check if a port is in use
check_port() {
    lsof -ti:$1 >/dev/null 2>&1
}

# Function to kill processes on a port
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}🔄 Killing existing processes on port $1${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Clean up any existing processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
kill_port 8001  # Backend
kill_port 8081  # Frontend Metro

# Start backend
echo -e "${BLUE}🚀 Starting Backend Server...${NC}"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup first.${NC}"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Start backend in background
python -m uvicorn test_server:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
for i in {1..15}; do
    if curl -s http://127.0.0.1:8001/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Test backend with a quick API call
echo -e "${BLUE}🧪 Testing backend...${NC}"
HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8001/health)
echo -e "${GREEN}✅ Backend health: $HEALTH_RESPONSE${NC}"

# Start frontend
echo -e "${BLUE}📱 Starting Mobile App...${NC}"
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Starting Expo development server...${NC}"
echo -e "${PURPLE}📱 Choose your experience:${NC}"
echo -e "${BLUE}   • Press 'i' for iOS Simulator${NC}"
echo -e "${BLUE}   • Press 'a' for Android Emulator${NC}"
echo -e "${BLUE}   • Press 'w' for Web Browser${NC}"
echo -e "${BLUE}   • Scan QR code with Expo Go app${NC}"

# Start Expo (this will block)
npx expo start

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill_port 8001
    kill_port 8081
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

echo -e "${PURPLE}🎉 Resilience App is ready!${NC}"
echo -e "${GREEN}Backend: http://127.0.0.1:8001${NC}"
echo -e "${GREEN}Frontend: http://localhost:8081${NC}"