#
from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import MemoryDep
from app.api.schemas.memory import (
    MemoryCreateRequest,
    MemorySearchRequest,
    MemoryResponse,
)

router = APIRouter()

@router.post(
    "/",
    response_model=MemoryResponse,
)
async def create_memory(
    request: MemoryCreateRequest,
    memory: MemoryDep,
):

    item = await memory.store(

        session_id=request.session_id,

        content=request.content,

        metadata=request.metadata,
    )

    return MemoryResponse.model_validate(
        item
    )
@router.get("/{memory_id}")
async def get_memory(
    memory_id: str,
    memory: MemoryDep,
):

    return await memory.get(
        memory_id,
    )
@router.get("/session/{session_id}")
async def session_memory(
    session_id: str,
    memory: MemoryDep,
):

    return await memory.history(
        session_id,
    )
@router.post("/search")
async def search(
    request: MemorySearchRequest,
    memory: MemoryDep,
):

    results = await memory.search(

        query=request.query,

        top_k=request.top_k,

        session_id=request.session_id,
    )

    return results
@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    memory: MemoryDep,
):

    await memory.delete(
        memory_id,
    )

    return {
        "success": True,
    }

@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    memory: MemoryDep,
):

    await memory.clear(
        session_id,
    )

    return {
        "success": True,
    }
@router.get("/long-term")
async def long_term(
    memory: MemoryDep,
):

    return await memory.long_term()
@router.post("/{memory_id}/promote")
async def promote(
    memory_id: str,
    memory: MemoryDep,
):

    await memory.promote(
        memory_id,
    )

    return {
        "success": True,
    }
@router.post("/{memory_id}/demote")
async def demote(
    memory_id: str,
    memory: MemoryDep,
):

    await memory.demote(
        memory_id,
    )

    return {
        "success": True,
    }
@router.post("/reindex")
async def reindex(
    memory: MemoryDep,
):

    task = await memory.rebuild_index()

    return {
        "task_id": task.id,
    }
@router.get("/stats")
async def stats(
    memory: MemoryDep,
):

    return await memory.stats()