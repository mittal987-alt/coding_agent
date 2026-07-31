#
from __future__ import annotations
from fastapi.responses import StreamingResponse
from fastapi import APIRouter

from app.api.dependencies import ToolRegistryDep
from app.api.schemas.tools import (
    ToolExecuteRequest,
    ToolExecuteResponse,
)

router = APIRouter()
@router.get(
    "/",
    summary="List registered tools",
)
async def list_tools(
    tools: ToolRegistryDep,
):

    return await tools.list_tools()
@router.get("/{tool_name}")
async def tool_info(
    tool_name: str,
    tools: ToolRegistryDep,
):

    return await tools.get_tool(
        tool_name,
    )
@router.post(
    "/execute",
    response_model=ToolExecuteResponse,
)
async def execute(
    request: ToolExecuteRequest,
    tools: ToolRegistryDep,
):

    result = await tools.execute(

        tool=request.tool,

        arguments=request.arguments,

        workspace=request.workspace,

        timeout=request.timeout,
    )

    return ToolExecuteResponse.model_validate(
        result,
    )@router.post("/stream")
async def stream_execute(
    request: ToolExecuteRequest,
    tools: ToolRegistryDep,
):

    async def generator():

        async for event in tools.stream(

            tool=request.tool,

            arguments=request.arguments,

            workspace=request.workspace,
        ):

            yield f"data: {event}\n\n"

    return StreamingResponse(

        generator(),

        media_type="text/event-stream",
    )
@router.post("/{execution_id}/cancel")
async def cancel(
    execution_id: str,
    tools: ToolRegistryDep,
):

    await tools.cancel(
        execution_id,
    )

    return {
        "success": True,
    }
@router.get("/{execution_id}/status")
async def status(
    execution_id: str,
    tools: ToolRegistryDep,
):

    return await tools.status(
        execution_id,
    )
@router.get("/{execution_id}/result")
async def result(
    execution_id: str,
    tools: ToolRegistryDep,
):

    return await tools.result(
        execution_id,
    )
@router.get("/history")
async def history(
    tools: ToolRegistryDep,
):

    return await tools.history()

@router.post("/reload")
async def reload_registry(
    tools: ToolRegistryDep,
):

    await tools.reload()

    return {
        "success": True,
    }
@router.post("/{tool_name}/validate")
async def validate(
    tool_name: str,
    tools: ToolRegistryDep,
):

    return await tools.validate(
        tool_name,
    )
@router.get("/{tool_name}/permissions")
async def permissions(
    tool_name: str,
    tools: ToolRegistryDep,
):

    return await tools.permissions(
        tool_name,
    )
