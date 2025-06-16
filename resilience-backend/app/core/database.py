from supabase import create_client, Client
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_supabase() -> Optional[Client]:
    """Get Supabase client instance"""
    try:
        if not settings.supabase_url or not settings.supabase_service_key:
            logger.error("Supabase credentials not configured")
            return None
            
        return create_client(
            settings.supabase_url, 
            settings.supabase_service_key
        )
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return None

# Global client instance
supabase_client = get_supabase()