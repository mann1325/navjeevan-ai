import asyncio

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.models.request_model import ChatRequest, ChatResponse
from backend.services.chat_service import process_chat_query

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse | Any:
    result = await asyncio.to_thread(process_chat_query, payload.query)
    if result.get("status") == "error":
        return JSONResponse(status_code=500, content=result)
    return ChatResponse(**result)
