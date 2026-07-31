"""
LangGraph Nodes

Each node executes one AI agent.
"""

from __future__ import annotations

from app.graph.state import AgentState


async def supervisor_node(
    state: AgentState,
    agent,
):

    return await agent.safe_run(state)


async def planner_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def repository_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def retriever_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def coder_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def reviewer_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def terminal_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def tester_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def git_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def memory_node(
    state,
    agent,
):

    return await agent.safe_run(state)


async def responder_node(
    state,
    agent,
):

    return await agent.safe_run(state)