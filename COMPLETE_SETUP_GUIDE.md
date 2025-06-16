# 🌟 Resilience App - Complete Setup Guide

**Experience the full user flow in 5 minutes!**

This guide will get you running the complete Resilience App so you can experience:
- Emotional reflection input with mood tracking
- AI-powered compassionate reframes  
- Personalized micro-win suggestions
- Progress tracking and streak building

## 🚀 Quick Start (Choose Your Experience)

### Option 1: Interactive Demo (Fastest - 2 minutes)
```bash
# Navigate to project
cd /Users/namankumar/Downloads/github/claude-project

# Start backend
cd resilience-backend
source venv/bin/activate
python -m uvicorn test_server:app --host 127.0.0.1 --port 8001 &

# Run interactive demo
cd ../ResilienceApp
node demo_simple.js
```

### Option 2: Mobile App on iOS Simulator (Full Experience)
```bash
# 1. Start backend
cd /Users/namankumar/Downloads/github/claude-project/resilience-backend
source venv/bin/activate
python -m uvicorn test_server:app --host 127.0.0.1 --port 8001 &

# 2. Start mobile app
cd ../ResilienceApp
npx expo start

# 3. Press 'i' to open iOS simulator
# 4. Experience the full user flow!
```

### Option 3: Web Version (Quick Testing)
```bash
# 1. Start backend
cd /Users/namankumar/Downloads/github/claude-project/resilience-backend
source venv/bin/activate
python -m uvicorn test_server:app --host 127.0.0.1 --port 8001 &

# 2. Start web version
cd ../ResilienceApp
npx expo start --web

# 3. Open http://localhost:8081 in your browser
```

---

## 📱 The Complete User Experience

Here's what you'll experience in the app:

### 1. **Home Screen** 🏠
- See your current streak (starts at 3 days)
- Tap **"What's going on right now?"** to begin

### 2. **Reflection Screen** 📝
- Share what's happening: *"I had a tough day and stress-ate. Feeling ashamed."*
- Select mood emoji: 😰
- Set intensity: 8/10
- Tap **"Share & Get Support"**

### 3. **AI Reframe Screen** 🤖
- Watch AI generate compassionate response
- Read validation: *"I hear you, and what you're experiencing is completely understandable..."*
- Tap **"Continue to Next Step"**

### 4. **Win Selection Screen** ✨
- See personalized micro-wins:
  - 🧘‍♀️ **Take 3 deep breaths** (2 min, mindfulness)
  - 🌸 **Drink a glass of water** (1 min, self-care)
- Tap a win to complete it

### 5. **Progress Update** 📈
- See mood improvement
- Watch streak continue
- Feel positive momentum!

---

## 🛠️ Detailed Setup Instructions

### Prerequisites
- Node.js installed
- Python 3.11+ installed
- Terminal access

### Step-by-Step Setup

#### 1. Backend Setup
```bash
# Navigate to backend
cd /Users/namankumar/Downloads/github/claude-project/resilience-backend

# Activate virtual environment
source venv/bin/activate

# Verify dependencies (should already be installed)
pip install -r requirements.txt

# Start the test server
python -m uvicorn test_server:app --host 127.0.0.1 --port 8001

# ✅ You should see: "Uvicorn running on http://127.0.0.1:8001"
```

#### 2. Test Backend (Optional)
```bash
# In a new terminal, test the API
curl http://127.0.0.1:8001/health

# ✅ Should return: {"status":"healthy","timestamp":"..."}
```

#### 3. Mobile App Setup
```bash
# Navigate to React Native app
cd /Users/namankumar/Downloads/github/claude-project/ResilienceApp

# Install dependencies (should already be done)
npm install

# Start Expo development server
npx expo start

# ✅ You should see the Expo dev tools
```

#### 4. Choose Your Platform

**For iOS Simulator:**
- Press `i` in the Expo terminal
- iOS Simulator will open with the app

**For Android Emulator:**
- Press `a` in the Expo terminal
- Android Emulator will open with the app

**For Web (Quick Test):**
- Press `w` in the Expo terminal
- Browser will open at http://localhost:8081

**For Physical Device:**
- Install Expo Go app on your phone
- Scan the QR code shown in terminal

---

## 🎯 What To Experience

### Core User Journey (5 minutes)
1. **Open the app** → See home screen with streak
2. **Tap "What's going on?"** → Go to reflection screen
3. **Write a reflection** → Share something you're struggling with
4. **Select mood** → Choose emoji and intensity
5. **Submit** → Watch AI generate compassionate response
6. **Read reframe** → Feel the validation and support
7. **Continue** → See personalized micro-win suggestions
8. **Complete a win** → Do a 2-minute action
9. **See progress** → Watch your streak and mood improve

### Key Features to Notice
- **Emotional Safety**: Non-judgmental, validating responses
- **Personalization**: Wins adapt to your mood and situation
- **Micro-Actions**: All wins are 2-5 minutes maximum
- **Progress Tracking**: Immediate positive reinforcement
- **Beautiful UI**: Calming colors and intuitive design

---

## 🐛 Troubleshooting

### Backend Issues
```bash
# If port 8001 is busy
lsof -ti:8001 | xargs kill -9

# If virtual environment issues
cd resilience-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Mobile App Issues
```bash
# If Expo won't start
npx expo start --clear

# If dependencies missing
npx expo install

# If iOS simulator won't open
# Install Xcode from App Store
```

### Network Issues
```bash
# Test backend connection
curl http://127.0.0.1:8001/health

# Check if both servers running
lsof -i :8001  # Backend
lsof -i :8081  # Frontend
```

---

## 📊 Quick Demo Alternative

If you want to see the flow without setup:

```bash
cd /Users/namankumar/Downloads/github/claude-project/ResilienceApp
node demo_simple.js
```

This runs a complete simulation showing:
- User opens app (streak: 3 days)
- Shares struggle about stress-eating
- Gets compassionate AI response
- Chooses "Take 3 deep breaths" micro-win
- Completes it and sees progress

---

## 🎉 Success Indicators

**You'll know it's working when:**
- ✅ Backend responds at http://127.0.0.1:8001/health
- ✅ Expo shows QR code and "Metro waiting on..."
- ✅ App opens showing "Good [morning/afternoon], How are you feeling?"
- ✅ You can navigate: Home → Reflection → Reframe → Wins
- ✅ API calls show in backend logs
- ✅ Data persists between screens

**The full experience should feel:**
- 🤗 **Emotionally safe** - Never judgmental
- ⚡ **Fast** - 2-3 seconds for AI responses
- 🎯 **Focused** - Clear next steps
- 💪 **Empowering** - Immediate progress

---

## 🚀 Ready to Experience It!

Choose your preferred method:
- **Quick Demo**: `node demo_simple.js`
- **Full Mobile**: `npx expo start` → press `i`
- **Web Test**: `npx expo start --web`

**The goal**: Experience how the app helps someone go from emotional struggle to positive momentum in under 5 minutes through AI-powered compassion and micro-wins.

Let me know which method you'd like to try! 📱✨