#
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends

from app.api.dependencies import get_container
from app.api.schemas.agent import (
    AgentRunRequest,
    AgentRunResponse,
    AgentStatusResponse,
)

router = APIRouter()

@router.post(
    "/run",
    response_model=AgentRunResponse,
    summary="Start an AI agent task",
)
async def run_agent(
    request: AgentRunRequest,
    container=Depends(get_container),
):
    """
    Launch a new autonomous task.
    """

    agent_manager = container.resolve("agent_manager")

    task = await agent_manager.start(

        goal=request.goal,

        workspace=request.workspace,

        model=request.model,

        context=request.context,
    )

    return AgentRunResponse(

        task_id=task.id,

        status=task.status,
    )
@router.get(
    "/status/{task_id}",
    response_model=AgentStatusResponse,
)
async def agent_status(
    task_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "agent_manager",
    )

    task = await manager.status(
        task_id,
    )

    if task is None:

        raise HTTPException(

            status_code=404,

            detail="Task not found.",
        )

    return AgentStatusResponse(

        task_id=task.id,

        status=task.status,

        progress=task.progress,

        current_step=task.current_step,
    )

@router.post(
    "/cancel/{task_id}",
)
async def cancel_agent(
    task_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "agent_manager",
    )

    success = await manager.cancel(
        task_id,
    )

    return {

        "success": success,
    }

@router.get(
    "/running",
)
async def running_agents(
    container=Depends(get_container),
):

    manager = container.resolve(
        "agent_manager",
    )

    return await manager.running()  

@router.get(
    "/result/{task_id}",
)
async def result(
    task_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "agent_manager",
    )

    result = await manager.result(
        task_id,
    )

    if result is None:

        raise HTTPException(

            status_code=404,

            detail="Task not completed.",
        )

    return result   

@router.get(
    "/logs/{task_id}",
)
async def logs(
    task_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "agent_manager",
    )

    return {

        "logs": await manager.logs(
            task_id,
        )
    }

@router.post(
    "/retry/{task_id}",
)
async def retry(
    task_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "agent_manager",
    )

    new_task = await manager.retry(
        task_id,
    )

    return {

        "task_id": new_task.id,
    }
