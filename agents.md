# Agents Overview

This document describes the three GPT-powered agents used in the project.

## ReframeAgent (GPT-4o)
- **Purpose**: Generate a positive reframe for a user reflection and suggest helpful micro wins.
- **Input JSON**:
  ```json
  { "text": "string", "mood": "string | null" }
  ```
- **Output JSON**:
  ```json
  { "reflection_id": int, "text": "string", "suggested_wins": ["string"] }
  ```
- **Tools**: `user_history_fingerprint`, `analyze_emotion`, `suggested_wins`.
- Use GPT-4o to produce concise encouragement and actionable suggestions.

## WinAgent (GPT-3.5)
- **Purpose**: Record a micro win and update the user's streak.
- **Input JSON**:
  ```json
  { "reflection_id": int, "win": "string" }
  ```
- **Output JSON**:
  ```json
  { "status": "recorded" }
  ```
- **Tools**: `suggested_wins`, `get_user_fingerprint`.
- Optimized for speed using GPT-3.5.

## ArcWatchAgent (GPT-4o)
- **Purpose**: Monitor user reflections over time to detect trends and surface insights.
- **Input JSON**:
  ```json
  { "history": ["string"] }
  ```
- **Output JSON**:
  ```json
  { "summary": "string", "emotional_trend": "string" }
  ```
- **Tools**: `user_history_fingerprint`, `analyze_emotion`.
- Uses GPT-4o for richer summaries and emotional analysis.
