# Backend Service

This directory contains the FastAPI backend for the Codex Project Plan. It provides endpoints used by the mobile app and exposes tools for GPT-driven agents.

## Local Setup (macOS)

1. Install Python through Homebrew:
   ```bash
   brew install python
   ```
2. Install dependencies with Poetry:
   ```bash
   cd backend
   poetry install
   ```
   Poetry's package mode is disabled so the project is installed in editable mode.

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=<your key>
DATABASE_URL=<postgres connection url>
```

## Running

Start the API with Uvicorn:

```bash
poetry run uvicorn app.main:app --reload
```

Run the test suite:

```bash
poetry run pytest
```

## API Routes

- `GET /health` – simple health check.
- `POST /reflections` – submit a reflection text and optional mood.
- `GET /reframe/{id}` – fetch an AI-generated reframe and suggested wins for a reflection.
- `POST /wins` – record completion of a micro win.
- `GET /streak` – return the current win streak count.
- `GET /winrack` – list all recorded wins.

## Deployment to Fly.io

1. Install the Fly CLI and log in.
2. Run `fly launch` inside `backend` to create the app.
3. Set required secrets:
   ```bash
   fly secrets set OPENAI_API_KEY=<your key> DATABASE_URL=<postgres url>
   ```
4. Deploy:
   ```bash
   fly deploy
   ```
