"""
Reviewer Agent

Reviews generated code edits.
"""

from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.prompts.reviewer import (
    REVIEWER_SYSTEM_PROMPT,
    REVIEWER_USER_TEMPLATE,
)

from app.review.models import ReviewResult


class ReviewerAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(
            llm=llm,
            name="Reviewer",
        )

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        prompt = REVIEWER_USER_TEMPLATE.format(

            request=state.user_request,

            plan=state.plan,

            changes=state.code_edits,

            context=state.retrieval_prompt,

        )

        response = await self.invoke_llm(

            REVIEWER_SYSTEM_PROMPT,

            prompt,

        )

        data = json.loads(response)

        review = ReviewResult.model_validate(data)

        state.review = review.summary

        state.review_passed = review.approved

        state.review_issues = review.issues

        return state