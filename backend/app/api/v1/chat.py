from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import json
import re
import os

from app.bootstrap.container import container
from app.llm.provider import ChatMessage, MessageRole, ChatRequest
from app.llm.router import TaskType, RouteRequest
from app.tools.filesystem.writer import FileWriter
from app.utils.storage_manager import StorageManager
from app.coding.config.settings import settings as _app_settings

router = APIRouter()
storage = StorageManager()
file_writer = FileWriter()

CODING_SYSTEM_PROMPT = """You are an expert AI coding assistant embedded in a developer workspace.

Answer the user's questions in a clear, helpful manner using standard Markdown. 

When the user asks you to create, modify, or generate code files, you MUST include a JSON block at the VERY END of your response containing the file modifications. Use this exact format:
```json
{
  "files": [
    {
      "path": "relative/path/to/file.py",
      "content": "full complete file content here"
    }
  ]
}
```

CRITICAL RULES FOR FILE MODIFICATIONS & PRESERVING EXISTING CODE:
- When modifying an EXISTING file (provided in the workspace context):
  1. Read the provided file's existing source code in the context carefully.
  2. Your output `content` MUST BE THE FULL, ENTIRE FILE from top to bottom.
  3. You MUST PRESERVE ALL existing code, imports, exports, state, hooks, functions, components, types, and styles.
  4. Merge your new feature additions seamlessly into the existing code at the proper locations.
  5. Remove ONLY the specific lines that need to be removed or replaced.
  6. NEVER output truncated files, partial code snippets (e.g., starting mid-function or starting at line 25), or placeholder comments like "// rest of existing code...".
  7. Your output will REPLACE the existing file on disk. Omitting existing code will DESTROY the user's file. Always output 100% complete files!
- File paths must be relative (e.g. "app/(app)/ads/page.tsx", "src/utils.py"). Never use absolute paths.
- If no files need to be modified or written, answer normally in Markdown and do not include the JSON block.
"""


class ChatRequestPayload(BaseModel):
    messages: List[dict]
    model: str = "gpt-4o"
    temperature: float = 0.2
    project_id: Optional[str] = None
    require_plan: bool = False
    approved_plan: Optional[str] = None


def _extract_json_from_text(text: str) -> Optional[dict]:
    """Try to parse a JSON object from LLM output, even if surrounded by markdown fences."""
    text = text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        # Try to find a JSON object or array within the text
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None


def _smart_merge_code(existing_content: str, new_content: str) -> str:
    """
    Intelligently merge new LLM code output into existing file content if the LLM outputted
    a partial snippet or truncated fragment.
    """
    if not existing_content.strip():
        return new_content

    existing_lines = existing_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    # Check for header/import loss or abrupt starting fragments
    existing_imports = [line for line in existing_lines if line.strip().startswith(("import ", "'use client'", '"use client"', "from ", "type ", "interface "))]
    new_imports = [line for line in new_lines if line.strip().startswith(("import ", "'use client'", '"use client"', "from "))]

    has_header_loss = bool(existing_imports) and not bool(new_imports)
    starts_abruptly = new_lines and (
        new_lines[0].strip().startswith("},") or
        new_lines[0].strip().startswith("];") or
        new_lines[0].strip().startswith("return") or
        new_lines[0].strip().startswith("<") or
        (new_lines[0].strip().startswith("export default function") and len(new_lines) > 1 and new_lines[1].strip().startswith("},"))
    )

    if has_header_loss or starts_abruptly:
        # Find header lines in existing_content before the main export/function
        header_lines = []
        for line in existing_lines:
            header_lines.append(line)
            if "export default" in line or "export function" in line or "export const" in line:
                break
        
        abrupt_match = None
        if new_lines:
            first_non_empty = next((l.strip() for l in new_lines if l.strip()), "")
            for idx, ex_line in enumerate(existing_lines):
                if first_non_empty and first_non_empty in ex_line:
                    abrupt_match = idx
                    break
        
        if abrupt_match is not None and abrupt_match > 0:
            return "".join(existing_lines[:abrupt_match]) + new_content
        else:
            missing_header = "".join([l for l in header_lines if l not in new_content])
            return missing_header + "\n" + new_content

    return new_content


def _build_project_context(project_id: str, messages: list) -> str:
    """Build repository file tree and inject full content of relevant existing files into prompt context."""
    repo_path = storage.repository_path(project_id)
    if not repo_path.exists():
        return ""

    tree = []
    file_map: dict[str, Path] = {}
    
    for root, _, files in os.walk(repo_path):
        if any(x in root for x in [".git", "node_modules", ".venv", "__pycache__", ".next", "dist", "build"]):
            continue
        rel_root = os.path.relpath(root, repo_path)
        if rel_root == ".":
            rel_root = ""
        for file in files:
            rel_p = os.path.join(rel_root, file).replace("\\", "/").lstrip("/")
            tree.append(rel_p)
            file_map[rel_p] = Path(root) / file

    if not tree:
        return ""

    user_prompt_text = " ".join([
        m.get("content", "") if isinstance(m.get("content"), str) else ""
        for m in messages if m.get("role") == "user"
    ]).lower()

    relevant_files: list[str] = []
    for rel_p in tree:
        p_lower = rel_p.lower()
        basename = os.path.basename(p_lower)
        name_no_ext = os.path.splitext(basename)[0]

        if rel_p in user_prompt_text or basename in user_prompt_text:
            relevant_files.append(rel_p)
        elif any(kw in user_prompt_text for kw in [name_no_ext, "filter", "ad", "page", "card", "grid", "route", "search"]) and len(name_no_ext) > 2:
            if p_lower.endswith((".tsx", ".ts", ".jsx", ".js", ".py", ".html", ".css", ".json")):
                relevant_files.append(rel_p)

    selected_files = list(dict.fromkeys(relevant_files))[:15]

    if not selected_files:
        for rel_p in tree:
            if rel_p.endswith((".tsx", ".ts", ".jsx", ".js", ".py")) and ("app/" in rel_p or "components/" in rel_p or "src/" in rel_p):
                selected_files.append(rel_p)
                if len(selected_files) >= 10:
                    break

    context_parts = [f"Current Project Files in Workspace:\n" + "\n".join(sorted(tree))]

    if selected_files:
        context_parts.append("\nEXISTING SOURCE CODE OF RELEVANT WORKSPACE FILES (Use this code to merge changes fully and preserve all existing functionality):")
        for rel_p in selected_files:
            file_path = file_map.get(rel_p)
            if file_path and file_path.exists():
                try:
                    size = file_path.stat().st_size
                    if size < 50000:
                        content = file_path.read_text(encoding="utf-8", errors="replace")
                        context_parts.append(f"\n--- FILE: {rel_p} ---\n{content}\n--- END FILE ---")
                except Exception:
                    pass

    return "\n".join(context_parts)


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
        if not str(target).startswith(str(repo_path.resolve())):
            continue

        if target.exists():
            try:
                existing_content = target.read_text(encoding="utf-8", errors="replace")
                content = _smart_merge_code(existing_content, content)
            except Exception:
                pass

        file_writer.write(target, content)
        written.append(rel_path)
    return written


def _load_project_api_keys(project_id: str) -> dict:
    """Load saved API keys for a project. Returns {provider_lower: key_value}."""
    # Keys are stored at storage/projects/{id}/config/api_keys.json
    keys_file = storage.project_path(project_id) / "config" / "api_keys.json"
    if not keys_file.exists():
        return {}
    try:
        raw = json.loads(keys_file.read_text())
        result = {}
        for entry in raw:
            provider = entry.get("provider", "").lower()
            value = entry.get("key_value", "")
            if provider and value:
                result[provider] = value
        return result
    except Exception:
        return {}


def _get_api_key(keys: dict, provider: str, settings_attr: str) -> str:
    """Get API key from project keys, then settings object (.env), then os.environ."""
    # 1. Check project-level saved API keys
    for k, v in keys.items():
        if provider in k:
            return v
    # 2. Fall back to .env / environment via Settings object
    val = getattr(_app_settings, settings_attr, None)
    if val:
        return val
    # 3. Final fallback to raw os.environ (in case loaded externally)
    return os.getenv(settings_attr, "")


@router.post("/")
async def chat_endpoint(payload: ChatRequestPayload):
    if not container.llm_manager:
        raise HTTPException(status_code=500, detail="LLM Manager is not initialized")

    system_prompt = CODING_SYSTEM_PROMPT
    if payload.project_id:
        proj_ctx = _build_project_context(payload.project_id, payload.messages)
        if proj_ctx:
            system_prompt += "\n\n" + proj_ctx

    # Build message list with coding system prompt prepended
    all_messages: List[ChatMessage] = [
        ChatMessage(role=MessageRole("system"), content=system_prompt)
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
        elif parsed and isinstance(parsed, list):
            message = raw_text
            files_to_write = parsed
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


@router.post("/stream")
async def chat_stream_endpoint(payload: ChatRequestPayload):
    """
    SSE streaming chat endpoint.
    Emits: data: {"type": "token"|"activity"|"done"|"error", ...}
    """
    import httpx as _httpx

    project_id = payload.project_id
    model = payload.model or "qwen2.5-coder:1.5b"

    # Load project API keys
    project_keys: dict = {}
    if project_id:
        project_keys = _load_project_api_keys(project_id)

    # Format messages: strip images, drop empty assistant messages (Mistral rejects them)
    messages = []
    for msg in payload.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
            content = " ".join(text_parts)
        # Skip assistant messages with no content — they cause 400 errors on all providers
        if role == "assistant" and not content.strip():
            continue
        messages.append({"role": role, "content": content})

    # Ensure conversation doesn't start with an assistant turn (some providers reject this)
    while messages and messages[0].get("role") == "assistant":
        messages.pop(0)

    # Inject context
    project_context = ""
    if project_id:
        project_context = "\n\n" + _build_project_context(project_id, payload.messages)

    # Add the system message at the top
    system_msg = CODING_SYSTEM_PROMPT + project_context
    messages.insert(0, {"role": "system", "content": system_msg})


    async def generate():
        full_response = ""

        def _sse(obj: dict) -> str:
            return "data: " + json.dumps(obj) + "\n\n"

        def _api_err(provider: str, status: int, body: bytes) -> str:
            msg = f"{provider} API Error {status}: {body.decode('utf-8', errors='replace')}"
            return _sse({"type": "error", "message": msg})

        yield _sse({"type": "activity", "step": "Connecting to AI\u2026"})

        try:
            # ── Mistral ──────────────────────────────────────────────────────
            if "mistral" in model.lower():
                api_key = _get_api_key(project_keys, "mistral", "MISTRAL_API_KEY")
                if not api_key:
                    yield _sse({"type": "error", "message": "No Mistral API key found. Please add it in project Settings \u2192 API Keys."})
                    return

                async with _httpx.AsyncClient(timeout=90) as client:
                    async with client.stream(
                        "POST",
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"model": model, "messages": messages, "temperature": payload.temperature, "stream": True},
                    ) as resp:
                        if resp.status_code != 200:
                            err = await resp.aread()
                            yield _api_err("Mistral", resp.status_code, err)
                            return
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            raw = line[6:]
                            if raw.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(raw)
                                token = chunk["choices"][0]["delta"].get("content", "")
                                if token:
                                    full_response += token
                                    yield _sse({"type": "token", "content": token})
                            except Exception:
                                pass

            # ── OpenAI ───────────────────────────────────────────────────────
            elif "gpt" in model.lower() or "openai" in model.lower():
                api_key = _get_api_key(project_keys, "openai", "OPENAI_API_KEY")
                if not api_key:
                    yield _sse({"type": "error", "message": "No OpenAI API key found. Please add it in project Settings \u2192 API Keys."})
                    return

                async with _httpx.AsyncClient(timeout=90) as client:
                    async with client.stream(
                        "POST",
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"model": model, "messages": messages, "temperature": payload.temperature, "stream": True},
                    ) as resp:
                        if resp.status_code != 200:
                            err = await resp.aread()
                            yield _api_err("OpenAI", resp.status_code, err)
                            return
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            raw = line[6:]
                            if raw.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(raw)
                                token = chunk["choices"][0]["delta"].get("content", "")
                                if token:
                                    full_response += token
                                    yield _sse({"type": "token", "content": token})
                            except Exception:
                                pass

            # ── Anthropic / Claude ───────────────────────────────────────────
            elif "claude" in model.lower() or "anthropic" in model.lower():
                api_key = _get_api_key(project_keys, "anthropic", "ANTHROPIC_API_KEY")
                if not api_key:
                    yield _sse({"type": "error", "message": "No Anthropic API key found. Please add it in project Settings \u2192 API Keys."})
                    return

                sys_msgs = [m["content"] for m in messages if m.get("role") == "system"]
                chat_msgs = [m for m in messages if m.get("role") != "system"]
                payload_data: dict = {"model": model, "max_tokens": 4096, "messages": chat_msgs, "stream": True}
                if sys_msgs:
                    payload_data["system"] = "\n".join(sys_msgs)

                async with _httpx.AsyncClient(timeout=90) as client:
                    async with client.stream(
                        "POST",
                        "https://api.anthropic.com/v1/messages",
                        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                        json=payload_data,
                    ) as resp:
                        if resp.status_code != 200:
                            err = await resp.aread()
                            yield _api_err("Anthropic", resp.status_code, err)
                            return
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            try:
                                data = json.loads(line[6:])
                                if data.get("type") == "content_block_delta":
                                    token = data.get("delta", {}).get("text", "")
                                    if token:
                                        full_response += token
                                        yield _sse({"type": "token", "content": token})
                            except Exception:
                                pass

            # ── Gemini ───────────────────────────────────────────────────────
            elif "gemini" in model.lower():
                api_key = _get_api_key(project_keys, "gemini", "GEMINI_API_KEY")
                if not api_key:
                    yield _sse({"type": "error", "message": "No Gemini API key found. Please add it in project Settings \u2192 API Keys."})
                    return

                gemini_messages = []
                for m in messages:
                    role = "user" if m["role"] in ("user", "system") else "model"
                    gemini_messages.append({"role": role, "parts": [{"text": m["content"]}]})

                gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}&alt=sse"
                async with _httpx.AsyncClient(timeout=90) as client:
                    async with client.stream(
                        "POST",
                        gemini_url,
                        headers={"Content-Type": "application/json"},
                        json={"contents": gemini_messages, "generationConfig": {"temperature": payload.temperature}},
                    ) as resp:
                        if resp.status_code != 200:
                            err = await resp.aread()
                            yield _api_err("Gemini", resp.status_code, err)
                            return
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            try:
                                data = json.loads(line[6:])
                                token = data["candidates"][0]["content"]["parts"][0].get("text", "")
                                if token:
                                    full_response += token
                                    yield _sse({"type": "token", "content": token})
                            except Exception:
                                pass

            # ── Ollama (local) ───────────────────────────────────────────────
            elif "ollama" in model.lower() or ":" in model or any(m in model.lower() for m in ["qwen", "llama", "deepseek", "codellama"]):
                ollama_model = model.replace("ollama/", "").replace("ollama:", "")
                try:
                    async with _httpx.AsyncClient(timeout=120) as client:
                        async with client.stream(
                            "POST",
                            "http://localhost:11434/api/chat",
                            json={"model": ollama_model, "messages": messages, "stream": True},
                        ) as resp:
                            if resp.status_code != 200:
                                err = await resp.aread()
                                yield _api_err("Ollama", resp.status_code, err)
                                return
                            async for line in resp.aiter_lines():
                                try:
                                    data = json.loads(line)
                                    token = data.get("message", {}).get("content", "")
                                    if token:
                                        full_response += token
                                        yield _sse({"type": "token", "content": token})
                                except Exception:
                                    pass
                except (_httpx.ConnectError, _httpx.ConnectTimeout):
                    mistral_key = _get_api_key(project_keys, "mistral", "MISTRAL_API_KEY")
                    openai_key = _get_api_key(project_keys, "openai", "OPENAI_API_KEY")
                    gemini_key = _get_api_key(project_keys, "gemini", "GEMINI_API_KEY")

                    if mistral_key:
                        yield _sse({"type": "activity", "step": "Local Ollama offline. Falling back to Mistral Cloud API…"})
                        try:
                            async with _httpx.AsyncClient(timeout=90) as client:
                                async with client.stream(
                                    "POST",
                                    "https://api.mistral.ai/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {mistral_key}", "Content-Type": "application/json"},
                                    json={"model": "mistral-small-latest", "messages": messages, "temperature": payload.temperature, "stream": True},
                                ) as resp:
                                    if resp.status_code == 200:
                                        async for line in resp.aiter_lines():
                                            if not line.startswith("data: "):
                                                continue
                                            raw = line[6:]
                                            if raw.strip() == "[DONE]":
                                                break
                                            try:
                                                chunk = json.loads(raw)
                                                token = chunk["choices"][0]["delta"].get("content", "")
                                                if token:
                                                    full_response += token
                                                    yield _sse({"type": "token", "content": token})
                                            except Exception:
                                                pass
                                        return
                        except Exception:
                            pass

                    elif openai_key:
                        yield _sse({"type": "activity", "step": "Local Ollama offline. Falling back to OpenAI GPT-4o…"})
                        try:
                            async with _httpx.AsyncClient(timeout=90) as client:
                                async with client.stream(
                                    "POST",
                                    "https://api.openai.com/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                                    json={"model": "gpt-4o", "messages": messages, "temperature": payload.temperature, "stream": True},
                                ) as resp:
                                    if resp.status_code == 200:
                                        async for line in resp.aiter_lines():
                                            if not line.startswith("data: "):
                                                continue
                                            raw = line[6:]
                                            if raw.strip() == "[DONE]":
                                                break
                                            try:
                                                chunk = json.loads(raw)
                                                token = chunk["choices"][0]["delta"].get("content", "")
                                                if token:
                                                    full_response += token
                                                    yield _sse({"type": "token", "content": token})
                                            except Exception:
                                                pass
                                        return
                        except Exception:
                            pass

                    yield _sse({
                        "type": "error",
                        "message": (
                            "Could not connect to local Ollama server at http://localhost:11434. "
                            "Please ensure Ollama is installed and running (`ollama serve`), "
                            "or change the AI Model in Project Settings to a Cloud API model (e.g. Mistral)."
                        )
                    })
                    return

            else:
                yield _sse({"type": "error", "message": f"Unsupported model: {model}. Please use Mistral, OpenAI, Anthropic, Gemini, or Ollama."})
                return

        except Exception as exc:
            yield _sse({"type": "error", "message": str(exc)})
            return

        # Write any code files from the response if project is provided
        modified_files: List[str] = []
        if project_id and full_response:
            parsed = _extract_json_from_text(full_response)
            if parsed:
                if isinstance(parsed, dict):
                    files_to_write = parsed.get("files", [])
                elif isinstance(parsed, list):
                    files_to_write = parsed
                else:
                    files_to_write = []
                    
                if files_to_write:
                    modified_files = _write_project_files(project_id, files_to_write)

        yield _sse({"type": "done", "modified_files": modified_files, "phase": "execute"})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
