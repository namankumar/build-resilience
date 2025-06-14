# Codex Project Plan

This repository contains the code for a mobile-first behavior change app. The project uses React Native for a shared iOS/Android codebase and a FastAPI backend hosted on Fly.io.

Contributor guidelines are in `AGENTS.md`.

## Directory Structure

- `frontend/` – React Native application (to be initialized with Expo or React Native CLI).
- `backend/` – FastAPI service providing endpoints and agent tools.
- `docs/` – Documentation including architecture diagrams and prompt templates.

## Backend Endpoints

- `POST /reflections` – submit reflection text and mood.
- `GET /reframe/{id}` – retrieve an AI-generated reframe with micro-win suggestions.
- `POST /wins` – record completion of a win.
- `GET /streak` – fetch streak data.
- `GET /winrack` – retrieve stored wins for the user.

The backend will also expose internal tools for GPT-powered agents, such as the user history fingerprint and micro-win selector.

## Testing

Run backend tests using Poetry:

```bash
cd backend
poetry install --no-root
poetry run pytest
```

## Frontend

The `frontend` directory contains the Expo-based mobile app that talks to the FastAPI backend.
To run it locally:

```bash
cd frontend
npm install
npm start
```

To share the app, install the Expo CLI and publish:

```bash
npm install -g expo-cli
expo publish
```
