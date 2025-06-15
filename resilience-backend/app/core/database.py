from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    """Get Supabase client instance"""
    return create_client(
        settings.supabase_url, 
        settings.supabase_service_key
    )

# Global client instance
supabase_client = get_supabase() if settings.supabase_url else None