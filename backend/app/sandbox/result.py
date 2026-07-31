from pydantic import BaseModel


class ExecutionResult(BaseModel):

    success: bool

    exit_code: int

    stdout: str

    stderr: str

    duration: float

    artifacts: list[str] = []

    metrics: dict = {}