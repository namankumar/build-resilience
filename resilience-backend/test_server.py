"""
Simple test server to verify FastAPI setup without database dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from uuid import uuid4

app = FastAPI(
    title="Resilience App API - Test Server",
    description="Test version without database dependencies",
    version="1.0.0-test"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Resilience Recovery App API - Test Server", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Mock API endpoints for testing
@app.post("/api/v1/reflections/")
async def create_reflection_mock(reflection_data: dict):
    """Mock reflection creation"""
    return {
        "id": str(uuid4()),
        "content": reflection_data.get("content", "Mock reflection"),
        "mood_emoji": reflection_data.get("mood_emoji"),
        "mood_intensity": reflection_data.get("mood_intensity"),
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/reflections/")
async def get_reflections_mock():
    """Mock reflection list"""
    return [
        {
            "id": str(uuid4()),
            "content": "This is a mock reflection",
            "mood_emoji": "😔",
            "mood_intensity": 6,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

@app.post("/api/v1/reframes/generate")
async def generate_reframe_mock(request_data: dict):
    """Mock reframe generation"""
    return {
        "id": str(uuid4()),
        "content": "I hear you, and what you're experiencing is completely understandable. You're being brave by acknowledging these feelings. This moment doesn't define you - you have the strength to move through this.",
        "ai_model_used": "mock-model",
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/wins/suggest")
async def suggest_wins_mock():
    """Mock win suggestions"""
    return [
        {
            "id": str(uuid4()),
            "title": "Take 3 deep breaths",
            "description": "Ground yourself with mindful breathing",
            "category": "mindfulness",
            "estimated_minutes": 2
        },
        {
            "id": str(uuid4()),
            "title": "Drink a glass of water",
            "description": "A simple act of self-care",
            "category": "self-care",
            "estimated_minutes": 1
        }
    ]

@app.post("/api/v1/wins/complete")
async def complete_win_mock(completion_data: dict):
    """Mock win completion"""
    return {
        "id": str(uuid4()),
        "win_id": completion_data.get("win_id"),
        "reflection_id": completion_data.get("reflection_id"),
        "completed_at": datetime.utcnow().isoformat(),
        "notes": completion_data.get("notes"),
        "mood_after": completion_data.get("mood_after")
    }

@app.get("/api/v1/streaks/current")
async def get_current_streak_mock():
    """Mock current streak"""
    return {
        "current_streak": 3,
        "longest_streak": 7,
        "last_activity_date": datetime.utcnow().date().isoformat(),
        "is_active": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)