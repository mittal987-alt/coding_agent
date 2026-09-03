"""
Evaluator Agent for Self-Correction & Test-Driven Development (TDD) Loop.
Intercepts test execution outputs, extracts failure tracebacks, and formulates precise error context
to feed back into the Coder Agent for iterative self-correction loops.
"""

from __future__ import annotations

import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.graph.state import AgentState


class EvaluationSummary(BaseModel):
    passed: bool = Field(..., description="Whether the tests or code execution passed successfully")
    should_retry: bool = Field(..., description="Whether the workflow should route back to CoderAgent for correction")
    retry_count: int = Field(default=0, description="Current retry iteration count")
    failure_reason: str = Field(default="", description="Summary of root cause of failure")
    extracted_traceback: str = Field(default="", description="Extracted traceback or error log")
    feedback_for_coder: str = Field(default="", description="Actionable instructions for the Coder agent to fix the code")


EVALUATOR_SYSTEM_PROMPT = """
You are an expert Evaluator and Debugging AI Agent in an enterprise AI Software Engineer workflow.
Your role is to evaluate code execution logs, unit test outputs, compiler errors, and stack traces.

Analyze the test/execution results provided and return a JSON object with the following schema:
{
    "passed": true|false,
    "should_retry": true|false,
    "failure_reason": "Concise explanation of the failing test or exception",
    "extracted_traceback": "Key error messages, file names, line numbers, and tracebacks extracted from logs",
    "feedback_for_coder": "Specific, actionable step-by-step guidance for the Coder Agent to fix the defect"
}
"""


class EvaluatorAgent(BaseAgent):
    def __init__(self, llm, max_retries: int = 3):
        super().__init__(llm, "Evaluator")
        self.max_retries = max_retries

    async def run(self, state: AgentState) -> AgentState:
        # Check current state retry count
        current_retries = getattr(state, "retry_count", 0)

        # Check if tests passed or failed
        tests_passed = getattr(state, "tests_passed", True)
        test_output = getattr(state, "test_output", "") or getattr(state, "terminal_output", "")

        if tests_passed:
            state.should_retry = False
            state.evaluator_feedback = "All tests and execution checks passed successfully."
            return state

        # If retries exceeded
        if current_retries >= self.max_retries:
            state.should_retry = False
            state.evaluator_feedback = (
                f"Maximum self-correction retries ({self.max_retries}) reached. "
                f"Routing to human-in-the-loop or responder."
            )
            return state

        # Invoke LLM to evaluate error and formulate feedback
        eval_prompt = f"""
Current Retry Count: {current_retries} / {self.max_retries}
User Request: {state.user_request if hasattr(state, 'user_request') else ''}

Execution / Test Logs:
{test_output}
"""
        try:
            response = await self.invoke_llm(EVALUATOR_SYSTEM_PROMPT, eval_prompt)
            data = json.loads(response)
            
            evaluation = EvaluationSummary(
                passed=data.get("passed", False),
                should_retry=data.get("should_retry", True) and (current_retries < self.max_retries),
                retry_count=current_retries + 1,
                failure_reason=data.get("failure_reason", "Test failure"),
                extracted_traceback=data.get("extracted_traceback", ""),
                feedback_for_coder=data.get("feedback_for_coder", "Fix the failing tests based on traceback.")
            )

            # Update state attributes
            state.retry_count = current_retries + 1
            state.should_retry = evaluation.should_retry
            state.evaluator_feedback = evaluation.feedback_for_coder
            state.last_error_traceback = evaluation.extracted_traceback

        except Exception as e:
            # Fallback if evaluation parsing fails
            state.retry_count = current_retries + 1
            state.should_retry = (current_retries + 1) < self.max_retries
            state.evaluator_feedback = f"Execution failed: {test_output[:500]}"
            state.last_error_traceback = str(e)

        return state
