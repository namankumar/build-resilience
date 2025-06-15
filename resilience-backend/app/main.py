from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, reflections, reframes, wins, streaks, chat
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Resilience Recovery App API",
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(reflections.router, prefix="/api/v1")
app.include_router(reframes.router, prefix="/api/v1")
app.include_router(wins.router, prefix="/api/v1")
app.include_router(streaks.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Resilience Recovery App API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)