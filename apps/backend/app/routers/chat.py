from fastapi import APIRouter, HTTPException
from typing import List
from app.models.chat import ChatMessage, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """Send a message and get AI response"""
    try:
        response = await chat_service.process_message(message.content)
        return ChatResponse(
            content=response,
            sender="assistant",
            timestamp=None  # Will be set by the model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history")
async def get_chat_history():
    """Get chat history (placeholder for future implementation)"""
    return {"messages": []}

@router.get("/chat/pipeline-status")
async def get_pipeline_status():
    """Get status of Splunk processing pipeline"""
    try:
        status = chat_service.get_pipeline_status()
        return {
            "success": True,
            "pipeline_status": status,
            "message": "Pipeline status retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
