from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    supabase_url: str = ""
    supabase_service_key: str = ""
    
    # AI Models
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    
    # JWT
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    app_name: str = "Resilience App API"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()