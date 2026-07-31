from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import json
import re

from app.bootstrap.container import container
from app.llm.provider import ChatMessage, MessageRole, ChatRequest
from app.llm.router import TaskType, RouteRequest
from app.tools.filesystem.writer import FileWriter
from app.utils.storage_manager import StorageManager

router = APIRouter()
storage = StorageManager()
file_writer = FileWriter()

CODING_SYSTEM_PROMPT = """You are an expert AI coding assistant embedded in a developer workspace.

When the user asks you to create, modify, or generate code files, you MUST respond in the following JSON format:
{
  "message": "A clear explanation of what you did and how it works.",
  "files": [
    {
      "path": "relative/path/to/file.py",
      "content": "full file content here"
    }
  ]
}

Rules:
- Always include a helpful "message" explaining your work.
- If the request involves writing code/files, include them in "files".
- If the user is just asking a question (no file creation needed), respond with:
  {"message": "your answer here", "files": []}
- File paths must be relative (e.g. "app.py", "src/utils.py"). Never use absolute paths.
- Always write complete, working code. Never use placeholders like "# TODO" or "...".
- ONLY return valid JSON. Do not include any text outside the JSON object.
"""


class ChatRequestPayload(BaseModel):
    messages: List[dict]
    model: str = "gpt-4o"
    temperature: float = 0.2
    project_id: Optional[str] = None


def _extract_json_from_text(text: str) -> Optional[dict]:
    """Try to parse a JSON object from LLM output, even if surrounded by markdown fences."""
    text = text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        # Try to find a JSON object within the text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def _write_project_files(project_id: str, files: list) -> List[str]:
    """Write files to the project repository and return their relative paths."""
    repo_path = storage.repository_path(project_id)
    written = []
    for file_def in files:
        rel_path = file_def.get("path", "").strip().lstrip("/")
        content = file_def.get("content", "")
        if not rel_path or not content:
            continue
        target = (repo_path / rel_path).resolve()
        # Security: ensure the target stays inside the repo
        if not str(target).startswith(str(repo_path.resolve())):
            continue
        file_writer.write(target, content)
        written.append(rel_path)
    return written


@router.post("/")
async def chat_endpoint(payload: ChatRequestPayload):
    if not container.llm_manager:
        raise HTTPException(status_code=500, detail="LLM Manager is not initialized")

    # Build message list with coding system prompt prepended
    all_messages: List[ChatMessage] = [
        ChatMessage(role=MessageRole("system"), content=CODING_SYSTEM_PROMPT)
    ]
    for msg in payload.messages:
        role = msg.get("role", "user")
        if role not in ["user", "assistant", "system"]:
            role = "user"
        all_messages.append(ChatMessage(
            role=MessageRole(role),
            content=msg.get("content", "")
        ))

    try:
        llm = await container.llm_router.route(RouteRequest(
            task=TaskType.CODING,
            model=payload.model,
        ))

        tokenizer = container.llm_manager.tokenizer
        prepared = tokenizer.prepare_messages(all_messages)

        request = ChatRequest(
            model=llm.model,
            messages=prepared,
            temperature=payload.temperature,
            stream=False,
        )

        response = await llm.complete(request)
        raw_text = response.message.content

        # Try to parse structured JSON from the LLM output
        parsed = _extract_json_from_text(raw_text)

        if parsed and isinstance(parsed, dict):
            message = parsed.get("message", raw_text)
            files_to_write = parsed.get("files", [])
        else:
            # Fallback: treat entire output as the message with no file writes
            message = raw_text
            files_to_write = []

        # Write files to disk if a project_id is provided
        modified_files: List[str] = []
        if payload.project_id and files_to_write:
            modified_files = _write_project_files(payload.project_id, files_to_write)

        return {
            "success": True,
            "message": message,
            "modified_files": modified_files,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
