"""
AGENTS.md & Project Spec Auto-Discovery Parser.
Scans repository workspaces for project rules, architecture guidelines, test commands,
coding conventions, and prohibited dependencies defined in AGENTS.md, .cursorrules, CLAUDE.md, etc.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class ProjectSpecification(BaseModel):
    has_spec: bool = False
    source_file: Optional[str] = None
    architectural_rules: List[str] = Field(default_factory=list)
    coding_style_guidelines: List[str] = Field(default_factory=list)
    custom_test_commands: List[str] = Field(default_factory=list)
    prohibited_packages: List[str] = Field(default_factory=list)
    raw_content: str = ""


SPEC_FILENAMES = [
    "AGENTS.md",
    "AGENTS.txt",
    ".cursorrules",
    "CLAUDE.md",
    "GEMINI.md",
    "CONTRIBUTING.md"
]


class SpecParser:
    """Discovers and parses project specification and rule files in a workspace."""

    @classmethod
    def discover_and_parse(cls, workspace_path: str) -> ProjectSpecification:
        ws_path = Path(workspace_path)
        if not ws_path.exists():
            return ProjectSpecification(has_spec=False)

        for filename in SPEC_FILENAMES:
            target_path = ws_path / filename
            if target_path.is_file():
                try:
                    content = target_path.read_text(encoding="utf-8", errors="ignore")
                    return cls.parse_content(content, source_file=filename)
                except Exception:
                    continue

        return ProjectSpecification(has_spec=False)

    @classmethod
    def parse_content(cls, content: str, source_file: str = "AGENTS.md") -> ProjectSpecification:
        arch_rules = []
        style_rules = []
        test_cmds = []
        prohibited = []

        lines = content.splitlines()
        current_section = None

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()

            if lower.startswith("#") or lower.startswith("##"):
                if "arch" in lower or "structure" in lower:
                    current_section = "arch"
                elif "style" in lower or "convention" in lower or "format" in lower:
                    current_section = "style"
                elif "test" in lower or "cmd" in lower or "run" in lower:
                    current_section = "test"
                elif "prohibited" in lower or "ban" in lower or "avoid" in lower:
                    current_section = "prohibited"
                else:
                    current_section = "general"
                continue

            if stripped.startswith("- ") or stripped.startswith("* ") or stripped.startswith("1. "):
                item = stripped.lstrip("-*123456789. ").strip()
                if current_section == "arch":
                    arch_rules.append(item)
                elif current_section == "style":
                    style_rules.append(item)
                elif current_section == "test":
                    test_cmds.append(item)
                elif current_section == "prohibited":
                    prohibited.append(item)
                else:
                    style_rules.append(item)

        return ProjectSpecification(
            has_spec=True,
            source_file=source_file,
            architectural_rules=arch_rules,
            coding_style_guidelines=style_rules,
            custom_test_commands=test_cmds,
            prohibited_packages=prohibited,
            raw_content=content
        )
