#
from __future__ import annotations
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.api.dependencies import (
    LLMManagerDep,
    MemoryDep,
    ToolRegistryDep,
)
from app.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

router = APIRouter()

@router.post(
    "/",
    response_model=ChatResponse,
    summary="Chat completion",
)
async def chat(
    request: ChatRequest,
    llm: LLMManagerDep,
    memory: MemoryDep,
    tools: ToolRegistryDep,
):
    """
    Main chat endpoint.
    """

    history = await memory.load(
        request.session_id,
    )

    response = await llm.chat(

        message=request.message,

        history=history,

        tools=tools,

        stream=False,
    )

    await memory.save(

        session_id=request.session_id,

        user=request.message,

        assistant=response.content,
    )

    return ChatResponse(

        message=response.content,

        usage=response.usage,

        model=response.model,
    )
@router.post(
    "/stream",
)
async def stream_chat(
    request: ChatRequest,
    llm: LLMManagerDep,
    memory: MemoryDep,
    tools: ToolRegistryDep,
):

    history = await memory.load(
        request.session_id,
    )

    async def event_generator():

        full_response = ""

        async for token in llm.stream(

            message=request.message,

            history=history,

            tools=tools,
        ):

            full_response += token

            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        await memory.save(

            session_id=request.session_id,

            user=request.message,

            assistant=full_response,
        )

        yield f"data: {json.dumps({'type': 'done', 'modified_files': []})}\n\n"

    return StreamingResponse(

        event_generator(),

        media_type="text/event-stream",
    )
@router.post(
    "/reset",
)
async def reset_chat(
    session_id: str,
    memory: MemoryDep,
):

    await memory.clear(
        session_id,
    )

    return {
        "success": True,
    }
@router.get(
    "/history/{session_id}",
)
async def history(
    session_id: str,
    memory: MemoryDep,
):

    messages = await memory.load(
        session_id,
    )

    return {
        "messages": messages,
    }
@router.get(
    "/sessions",
)
async def sessions(
    memory: MemoryDep,
):

    return await memory.sessions()