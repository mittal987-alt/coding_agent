from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class BrowserAction(str, Enum):

    OPEN = "open"

    CLICK = "click"

    FILL = "fill"

    SCREENSHOT = "screenshot"

    CONTENT = "content"

    EVALUATE = "evaluate"

    CLOSE = "close"


class BrowserRequest(BaseModel):

    action: BrowserAction

    url: str | None = None

    selector: str | None = None

    text: str | None = None

    script: str | None = None

    path: str | None = None


class BrowserResult(BaseModel):

    success: bool

    output: str

    metadata: dict = {}