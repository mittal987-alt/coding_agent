from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

LogLevel = Literal[
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

LogFormat = Literal[
    "console",
    "json",
]

HandlerType = Literal[
    "console",
    "file",
]

@dataclass(slots=True)
class ConsoleHandlerConfig:
    """
    Console logging configuration.
    """

    enabled: bool = True

    level: LogLevel = "INFO"


@dataclass(slots=True)
class FileHandlerConfig:
    """
    File logging configuration.
    """

    enabled: bool = True

    directory: str = "logs"

    filename: str = "application.log"

    max_bytes: int = 10 * 1024 * 1024

    backup_count: int = 5

    level: LogLevel = "INFO"

@dataclass(slots=True)
class JsonLoggingConfig:
    """
    Structured JSON logging.
    """

    enabled: bool = False

    include_timestamp: bool = True

    include_level: bool = True

    include_logger: bool = True

    include_process: bool = True

    include_thread: bool = True

@dataclass(slots=True)
class RequestLoggingConfig:
    """
    HTTP request logging.
    """

    enabled: bool = True

    log_headers: bool = False

    log_body: bool = False

    log_response: bool = False

    correlation_id_header: str = "X-Request-ID"

@dataclass(slots=True)
class OpenTelemetryConfig:
    """
    OpenTelemetry integration.
    """

    enabled: bool = False

    service_name: str = "ai-software-engineer"

    exporter_endpoint: str | None = None

@dataclass(slots=True)
class LoggingConfig:
    """
    Complete logging configuration.
    """

    level: LogLevel = "INFO"

    format: LogFormat = "console"

    handlers: list[HandlerType] = field(
        default_factory=lambda: [
            "console",
            "file",
        ],
    )

    console: ConsoleHandlerConfig = field(
        default_factory=ConsoleHandlerConfig,
    )

    file: FileHandlerConfig = field(
        default_factory=FileHandlerConfig,
    )

    json: JsonLoggingConfig = field(
        default_factory=JsonLoggingConfig,
    )

    requests: RequestLoggingConfig = field(
        default_factory=RequestLoggingConfig,
    )

    telemetry: OpenTelemetryConfig = field(
        default_factory=OpenTelemetryConfig,
    )

def create_logging_config() -> LoggingConfig:
    """
    Create the default logging configuration.
    """
    return LoggingConfig()