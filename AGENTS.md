Use Poetry for backend dependencies. After modifying the backend:

```
cd backend
poetry install --no-root
```

Start the backend and frontend in separate terminals before running tests:

```
poetry run uvicorn app.main:app --reload
```

```
cd frontend
npm install
npm start
```

Then execute the tests:

```
cd backend
poetry run pytest -q
```
