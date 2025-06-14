# Architecture Overview

- **Frontend**: React Native app shared between iOS and Android. Future support for React Native Web.
- **Backend**: FastAPI service deployed on Fly.io.
- **Database**: Supabase (PostgreSQL) for storing user data and wins.
- **Agent Tools**: Python modules invoked by the backend for personalization (user history fingerprint, micro-win selector, streak updates).
- **Monitoring**: Sentry integration for both frontend and backend.

The current implementation uses in-memory storage for reflections and wins.
Agent tools are simple Python functions under `app/tools.py` used internally by
the backend to personalize responses.
