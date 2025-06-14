# Frontend

This directory contains the React Native frontend built with Expo. It communicates with the FastAPI backend running on `localhost:8000`.

## Development

```
cd frontend
npm install
npm start # starts the Expo development server
```

## Deployment

Install the Expo CLI if not already present:

```bash
npm install -g expo-cli
```

Publish the app to Expo:

```bash
expo publish
```

This will generate a shareable link for testers.
