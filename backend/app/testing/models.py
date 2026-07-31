from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class TestStatus(str, Enum):

    PASSED = "passed"

    FAILED = "failed"

    ERROR = "error"


class TestSuite(str, Enum):

    PYTEST = "pytest"

    JEST = "jest"

    FLUTTER = "flutter"

    UNKNOWN = "unknown"


class TestResult(BaseModel):

    suite: TestSuite

    status: TestStatus

    total: int

    passed: int

    failed: int

    skipped: int

    summary: str

    output: str