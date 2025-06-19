# Claude Project Documentation

## Project Structure

This is a full-stack resilience app with React Native frontend and Python FastAPI backend.

### Main Components

- **ResilienceApp/**: React Native frontend using Expo
- **resilience-backend/**: Python FastAPI backend with AI services

## ResilienceApp (Frontend)
- **Framework**: React Native with Expo SDK ~53.0.11
- **Target Platforms**: iOS, Android, Web
- **Key Dependencies**: 
  - React 19.0.0, React Native 0.79.3
  - @supabase/supabase-js for backend integration
  - @tanstack/react-query for data fetching
  - Zustand for state management
  - React Navigation for routing

### Frontend Structure
- `src/screens/`: Main app screens (Home, Reflection, Reframe, WinSelection)
- `src/services/`: API integration (Supabase, general API)
- `src/store/`: State management (app state, auth state)
- `src/types/`: TypeScript type definitions
- `web/`: Web-specific configurations
- `babel.config.js`: Babel configuration with import.meta transform
- `metro.config.js`: Metro bundler configuration

### Build Scripts
- `npm run start`: Start Expo development server
- `npm run web`: Start web development server
- `npm run android`: Start Android development server
- `npm run ios`: Start iOS development server

## resilience-backend (Backend)
- **Framework**: FastAPI Python backend
- **Services**: AI-powered chat, mood detection, reframe generation
- **Database**: Supabase integration
- **API Structure**: Versioned API (v1) with modular endpoints

### Backend Structure
- `app/api/v1/`: API endpoints (auth, chat, reflections, reframes, wins, streaks)
- `app/models/`: Database models
- `app/services/ai/`: AI services (chat assistant, mood detector, reframe agent, win generator)
- `app/core/`: Core configuration (database, security, config)
- `app/tests/`: Test files

## Known Issues
- **Web Build**: import.meta syntax error causing blank white screen on web
- **Solution**: babel-plugin-transform-import-meta is configured but may need cache clearing

## Development Commands
- Frontend: `cd ResilienceApp && npm run web`
- Backend: `cd resilience-backend && python -m uvicorn app.main:app --reload`
- Clear caches: `expo start --clear` or `npx metro --reset-cache`

## Environment Variables
Required in ResilienceApp:
- EXPO_PUBLIC_SUPABASE_URL
- EXPO_PUBLIC_SUPABASE_ANON_KEY  
- EXPO_PUBLIC_API_URL