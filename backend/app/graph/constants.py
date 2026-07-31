from enum import Enum


class AgentName(str, Enum):

    SUPERVISOR = "supervisor"

    PLANNER = "planner"

    REPOSITORY = "repository"

    RETRIEVER = "retriever"

    CODER = "coder"

    REVIEWER = "reviewer"

    TERMINAL = "terminal"

    TESTER = "tester"

    GIT = "git"

    MEMORY = "memory"

    RESPONDER = "responder"


    class WorkflowStatus(str, Enum):

    CREATED = "created"

    RUNNING = "running"

    WAITING = "waiting"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    MAX_REVIEW_RETRIES = 3

MAX_TEST_RETRIES = 3

MAX_TERMINAL_RETRIES = 2

MAX_WORKFLOW_RETRIES = 5


LLM_TIMEOUT = 120

TERMINAL_TIMEOUT = 300

TEST_TIMEOUT = 900

WORKFLOW_TIMEOUT = 3600


SUPPORTED_LANGUAGES = {

    "python",

    "javascript",

    "typescript",

    "go",

    "rust",

    "java",

    "cpp",

    "c",

    "dart",

    "kotlin",

    "swift",

    "php",

    "ruby",

    "html",

    "css",

    "sql",

    "yaml",

    "json",

    "markdown",
}

IGNORE_DIRECTORIES = {

    ".git",

    "__pycache__",

    "node_modules",

    ".next",

    ".venv",

    "venv",

    "dist",

    "build",

    ".idea",

    ".vscode",

    ".pytest_cache",

    ".mypy_cache",

    ".turbocache",

    "coverage",
}

DEFAULT_CHAT_MODEL = "qwen2.5-coder"

DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"

DEFAULT_REVIEW_MODEL = "qwen2.5-coder"

DEFAULT_PLANNER_MODEL = "qwen2.5-coder"



ENABLE_MEMORY = True

ENABLE_GIT = True

ENABLE_TERMINAL = True

ENABLE_TESTING = True

ENABLE_REVIEW = True

ENABLE_STREAMING = True

ENABLE_CHECKPOINTS = True

ENABLE_PARALLEL_RETRIEVAL = False

ALLOWED_TERMINAL_COMMANDS = {

    "pytest",

    "python",

    "pip",

    "npm",

    "pnpm",

    "yarn",

    "flutter",

    "dart",

    "go",

    "cargo",

    "git",
}

class EventName(str, Enum):

    WORKFLOW_STARTED = "workflow_started"

    WORKFLOW_FINISHED = "workflow_finished"

    AGENT_STARTED = "agent_started"

    AGENT_FINISHED = "agent_finished"

    ERROR = "error"

    CHECKPOINT = "checkpoint"


    WORKFLOW_NODES = [

    AgentName.SUPERVISOR,

    AgentName.PLANNER,

    AgentName.REPOSITORY,

    AgentName.RETRIEVER,

    AgentName.CODER,

    AgentName.REVIEWER,

    AgentName.TERMINAL,

    AgentName.TESTER,

    AgentName.GIT,

    AgentName.MEMORY,

    AgentName.RESPONDER,
]