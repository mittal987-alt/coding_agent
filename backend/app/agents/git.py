from __future__ import annotations

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.git.executor import GitExecutor

from app.prompts.git import GIT_SYSTEM_PROMPT


class GitAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(

            llm,

            "Git",

        )

        self.git = GitExecutor()

    async def run(

        self,

        state: AgentState,

    ) -> AgentState:

        await self.git.add()

        prompt = f"""
User Request

{state.user_request}

Plan

{state.plan}

Summary

{state.generated_code}
"""

        commit_message = await self.invoke_llm(

            GIT_SYSTEM_PROMPT,

            prompt,

        )

        result = await self.git.commit(

            commit_message.strip()

        )

        state.commit_hash = result.stdout

        state.git_commit_message = commit_message.strip()

        return state