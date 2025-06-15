from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from app.models.chat import (
    ChatSessionCreate, ChatSessionResponse, ChatMessageCreate, 
    ChatMessageResponse, ChatResponse, ChatStatus, ChatMode
)
from app.core.security import get_current_user
from app.core.database import get_supabase
from app.services.ai.chat_assistant import ChatAssistantAgent

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/start", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_chat_session(
    request: ChatSessionCreate,
    current_user: str = Depends(get_current_user)
):
    """Start a new chat session for a reflection"""
    try:
        supabase = get_supabase()
        
        # Verify reflection exists and belongs to user
        reflection_response = supabase.table("reflections").select("id").eq(
            "id", str(request.reflection_id)
        ).eq("user_id", current_user).execute()
        
        if not reflection_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        # Create chat session
        session_data = {
            "id": str(uuid4()),
            "user_id": current_user,
            "reflection_id": str(request.reflection_id),
            "status": ChatStatus.ACTIVE.value,
            "current_mode": ChatMode.LISTEN.value,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        
        response = supabase.table("chat_sessions").insert(session_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chat session"
            )
        
        return ChatSessionResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatMessageCreate,
    current_user: str = Depends(get_current_user)
):
    """Send a message in a chat session and get AI response"""
    try:
        supabase = get_supabase()
        
        # Verify session exists and belongs to user
        session_response = supabase.table("chat_sessions").select("*").eq(
            "id", str(request.session_id)
        ).eq("user_id", current_user).execute()
        
        if not session_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        session = session_response.data[0]
        
        if session["status"] != ChatStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chat session is not active"
            )
        
        # Save user message
        user_message_data = {
            "id": str(uuid4()),
            "session_id": str(request.session_id),
            "user_id": current_user,
            "role": "user",
            "content": request.message,
            "created_at": datetime.utcnow().isoformat()
        }
        
        user_msg_response = supabase.table("chat_messages").insert(user_message_data).execute()
        
        # Get conversation history
        history_response = supabase.table("chat_messages").select("*").eq(
            "session_id", str(request.session_id)
        ).order("created_at", desc=False).execute()
        
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history_response.data
        ]
        
        # Generate AI response
        chat_assistant = ChatAssistantAgent()
        ai_response = await chat_assistant.respond_to_message(
            request.message,
            conversation_history,
            session["current_mode"]
        )
        
        # Save AI response
        ai_message_data = {
            "id": str(uuid4()),
            "session_id": str(request.session_id),
            "user_id": current_user,
            "role": "assistant",
            "content": ai_response["content"],
            "ai_model_used": chat_assistant.model.value,
            "mood_analysis": ai_response["mood_analysis"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        ai_msg_response = supabase.table("chat_messages").insert(ai_message_data).execute()
        
        # Update session mode if changed
        if ai_response["mode"] != session["current_mode"]:
            supabase.table("chat_sessions").update({
                "current_mode": ai_response["mode"]
            }).eq("id", str(request.session_id)).execute()
        
        # Check if conversation should conclude
        conclusion_check = await chat_assistant.should_conclude_conversation(
            conversation_history
        )
        
        session_status = ChatStatus.ACTIVE
        conclusion_suggestion = None
        
        if conclusion_check["should_conclude"]:
            conclusion_suggestion = conclusion_check.get("suggested_closing")
            # Don't automatically end session, just suggest
        
        return ChatResponse(
            message=ChatMessageResponse(**ai_msg_response.data[0]),
            session_status=session_status,
            current_mode=ChatMode(ai_response["mode"]),
            should_conclude=conclusion_check["should_conclude"],
            conclusion_suggestion=conclusion_suggestion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )

@router.post("/{session_id}/complete", response_model=ChatSessionResponse)
async def complete_chat_session(
    session_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Mark a chat session as completed"""
    try:
        supabase = get_supabase()
        
        # Verify session exists and belongs to user
        session_response = supabase.table("chat_sessions").select("*").eq(
            "id", str(session_id)
        ).eq("user_id", current_user).execute()
        
        if not session_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Update session status
        response = supabase.table("chat_sessions").update({
            "status": ChatStatus.COMPLETED.value,
            "completed_at": datetime.utcnow().isoformat()
        }).eq("id", str(session_id)).execute()
        
        return ChatSessionResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Get all messages in a chat session"""
    try:
        supabase = get_supabase()
        
        # Verify session belongs to user
        session_response = supabase.table("chat_sessions").select("id").eq(
            "id", str(session_id)
        ).eq("user_id", current_user).execute()
        
        if not session_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get messages
        response = supabase.table("chat_messages").select("*").eq(
            "session_id", str(session_id)
        ).order("created_at", desc=False).execute()
        
        return [ChatMessageResponse(**msg) for msg in response.data]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )