from __future__ import annotations

import json
from pathlib import Path

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.prompts.tester import TESTER_SYSTEM_PROMPT

from app.testing.detector import TestDetector
from app.testing.executor import TestExecutor
from app.testing.models import TestSuite


class TesterAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(

            llm,

            "Tester",

        )

        self.detector = TestDetector()

        self.executor = TestExecutor()

    async def run(

        self,

        state: AgentState,

    ) -> AgentState:

        workspace = Path(

            state.repository.metadata.workspace_path

        )

        suite = self.detector.detect(

            workspace

        )

        if suite == TestSuite.PYTEST:

            result = await self.executor.run_pytest()

        elif suite == TestSuite.JEST:

            result = await self.executor.run_jest()

        elif suite == TestSuite.FLUTTER:

            result = await self.executor.run_flutter()

        else:

            state.tests_passed = False

            state.test_output = "No supported test framework."

            return state

        prompt = f"""

Test Output

{result.stdout}

"""

        response = await self.invoke_llm(

            TESTER_SYSTEM_PROMPT,

            prompt,

        )

        analysis = json.loads(

            response

        )

        state.test_output = analysis["summary"]

        state.tests_passed = analysis["passed"]

        state.test_recommendations = analysis.get(

            "recommendations",

            [],

        )

        return state