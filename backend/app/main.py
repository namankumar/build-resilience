from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# In-memory stores for demo purposes
reflections = {}
reframes = {}
wins = []
current_streak = 0

class ReflectionInput(BaseModel):
    text: str
    mood: Optional[str] = None

class Reflection(BaseModel):
    id: int
    text: str
    mood: Optional[str] = None

class Reframe(BaseModel):
    reflection_id: int
    text: str
    suggested_wins: List[str]

class Win(BaseModel):
    reflection_id: int
    win: str

class Streak(BaseModel):
    count: int

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/reflections", response_model=Reflection)
def create_reflection(payload: ReflectionInput):
    reflection_id = len(reflections) + 1
    reflection = Reflection(id=reflection_id, text=payload.text, mood=payload.mood)
    reflections[reflection_id] = reflection
    # Simulate AI reframe generation
    reframe_text = f"Reframe: {payload.text}"
    reframes[reflection_id] = Reframe(reflection_id=reflection_id, text=reframe_text, suggested_wins=["walk", "drink water"])
    return reflection

@app.get("/reframe/{reflection_id}", response_model=Reframe)
def get_reframe(reflection_id: int):
    if reflection_id not in reframes:
        raise HTTPException(status_code=404, detail="Reframe not found")
    return reframes[reflection_id]

@app.post("/wins")
def record_win(win: Win):
    global current_streak
    if win.reflection_id not in reflections:
        raise HTTPException(status_code=404, detail="Reflection not found")
    wins.append(win)
    current_streak += 1
    return {"status": "recorded"}

@app.get("/streak", response_model=Streak)
def get_streak():
    return Streak(count=current_streak)

@app.get("/winrack")
def get_winrack():
    return {"wins": [w.win for w in wins]}
