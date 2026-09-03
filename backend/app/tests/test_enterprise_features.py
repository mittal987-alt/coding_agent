"""
Unit tests for the enterprise feature implementations.

Tests:
  - AgentState field uniqueness (Phase 1 fix)
  - CheckpointManager save/load/delete/list_pending (Phase 1 fix)
  - WorkflowRouter routing logic (Phase 2 fix)
  - BM25 + RRF HybridRanker (Phase 5)
  - LineDiffEngine patch apply (existing)
  - MCPClientManager HTTP/STDIO tool registration (Phase 6)
  - EvaluationSummary / EvaluatorAgent (Phase 2)
  - SpecParser AGENTS.md parsing (Phase 4)
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# Phase 1: AgentState — no duplicate fields
# ---------------------------------------------------------------------------


class TestAgentState:
    def test_no_duplicate_fields(self):
        """AgentState must define each field exactly once."""
        from app.graph.state import AgentState

        fields = list(AgentState.model_fields.keys())
        assert len(fields) == len(set(fields)), (
            f"Duplicate fields found in AgentState: "
            f"{[f for f in fields if fields.count(f) > 1]}"
        )

    def test_required_fields_present(self):
        """All new enterprise fields must be present."""
        from app.graph.state import AgentState

        required_new_fields = [
            "hitl_pending", "hitl_node_id", "hitl_approved",
            "spec", "memory_count",
        ]
        model_fields = set(AgentState.model_fields.keys())
        for field in required_new_fields:
            assert field in model_fields, f"Missing required field: {field}"

    def test_defaults(self):
        """AgentState should instantiate with minimal args."""
        from app.graph.state import AgentState

        state = AgentState(user_request="test", workspace_id=1)
        assert state.hitl_pending is False
        assert state.hitl_approved is None
        assert state.retry_count == 0
        assert state.memory_count == 0
        assert state.code_edits == []
        assert state.tasks == []


# ---------------------------------------------------------------------------
# Phase 1: CheckpointManager
# ---------------------------------------------------------------------------


class TestCheckpointManager:
    def test_save_and_load(self, tmp_path):
        from app.graph.state import AgentState
        from app.graph.checkpoint import CheckpointManager

        mgr = CheckpointManager(checkpoint_dir=str(tmp_path))
        state = AgentState(user_request="fix bug", workspace_id=42)
        state.plan = "Step 1: fix. Step 2: test."
        state.retry_count = 2

        mgr.save("wf-001", state)
        loaded = mgr.load("wf-001")

        assert loaded is not None
        assert loaded.user_request == "fix bug"
        assert loaded.workspace_id == 42
        assert loaded.plan == "Step 1: fix. Step 2: test."
        assert loaded.retry_count == 2

    def test_load_nonexistent_returns_none(self, tmp_path):
        from app.graph.checkpoint import CheckpointManager

        mgr = CheckpointManager(checkpoint_dir=str(tmp_path))
        assert mgr.load("nonexistent-id") is None

    def test_delete(self, tmp_path):
        from app.graph.state import AgentState
        from app.graph.checkpoint import CheckpointManager

        mgr = CheckpointManager(checkpoint_dir=str(tmp_path))
        state = AgentState(user_request="x", workspace_id=1)
        mgr.save("wf-del", state)
        assert mgr.exists("wf-del")
        mgr.delete("wf-del")
        assert not mgr.exists("wf-del")

    def test_list_pending(self, tmp_path):
        from app.graph.state import AgentState
        from app.graph.checkpoint import CheckpointManager

        mgr = CheckpointManager(checkpoint_dir=str(tmp_path))

        s1 = AgentState(user_request="a", workspace_id=1)
        s1.hitl_pending = True
        s1.hitl_node_id = "git"

        s2 = AgentState(user_request="b", workspace_id=2)
        # hitl_pending defaults to False

        mgr.save("pending-wf", s1)
        mgr.save("normal-wf", s2)

        pending = mgr.list_pending()
        assert "pending-wf" in pending
        assert "normal-wf" not in pending


# ---------------------------------------------------------------------------
# Phase 2: WorkflowRouter
# ---------------------------------------------------------------------------


class TestWorkflowRouter:
    def _state(self, **kwargs):
        from app.graph.state import AgentState
        return AgentState(user_request="test", workspace_id=1, **kwargs)

    def test_routes_to_planner_when_no_plan(self):
        from app.graph.router import WorkflowRouter
        router = WorkflowRouter()
        state = self._state()
        assert router.route(state) == "planner"

    def test_routes_to_retriever_after_plan(self):
        from app.graph.router import WorkflowRouter
        router = WorkflowRouter()
        state = self._state(plan="do the thing", repository=MagicMock())
        assert router.route(state) == "retriever"

    def test_routes_to_coder_after_retrieval(self):
        from app.graph.router import WorkflowRouter
        router = WorkflowRouter()
        state = self._state(
            plan="plan",
            repository=MagicMock(),
            retrieval_prompt="context",
        )
        assert router.route(state) == "coder"

    def test_routes_to_evaluator_on_test_failure(self):
        from app.graph.router import WorkflowRouter
        router = WorkflowRouter()
        state = self._state(
            plan="plan",
            repository=MagicMock(),
            retrieval_prompt="ctx",
            code_edits=[MagicMock()],
            review="looks ok",
            review_passed=True,
            terminal_output="ok",
            test_output="FAILED",
            tests_passed=False,
            retry_count=0,
        )
        assert router.route(state) == "evaluator"

    def test_routes_to_responder_after_max_retries(self):
        from app.graph.router import WorkflowRouter, MAX_RETRIES
        router = WorkflowRouter()
        state = self._state(
            plan="plan",
            repository=MagicMock(),
            retrieval_prompt="ctx",
            code_edits=[MagicMock()],
            review="ok",
            review_passed=True,
            terminal_output="ok",
            test_output="FAIL",
            tests_passed=False,
            retry_count=MAX_RETRIES,
        )
        assert router.route(state) == "responder"

    def test_routes_to_git_after_tests_pass(self):
        from app.graph.router import WorkflowRouter
        router = WorkflowRouter()
        state = self._state(
            plan="plan",
            repository=MagicMock(),
            retrieval_prompt="ctx",
            code_edits=[MagicMock()],
            review="ok",
            review_passed=True,
            terminal_output="ok",
            test_output="passed",
            tests_passed=True,
        )
        assert router.route(state) == "git"

    def test_hitl_pending_blocks_routing(self):
        from app.graph.router import WorkflowRouter
        router = WorkflowRouter()
        state = self._state(
            plan="plan",
            hitl_pending=True,
            hitl_node_id="git",
            hitl_approved=None,
        )
        result = router.route(state)
        assert result == "git"  # blocked at git node


# ---------------------------------------------------------------------------
# Phase 5: BM25 + RRF HybridRanker
# ---------------------------------------------------------------------------


class TestHybridRanker:
    def _make_result(self, chunk_id: str, content: str, score: float = 0.5, symbol=None):
        from app.retrieval.models import RetrievalResult, RetrievalSource
        from app.embeddings.chunk_models import CodeChunk

        chunk = CodeChunk(
            id=chunk_id,
            workspace_id=1,
            file="test.py",
            content=content,
            symbol=symbol,
            kind="function",
            start_line=1,
            end_line=10,
        )
        return RetrievalResult(
            chunk=chunk,
            score=score,
            source=RetrievalSource.VECTOR,
            metadata={"num_sources": 1},
        )

    def test_returns_sorted_by_rrf(self):
        from app.retrieval.ranker import HybridRanker

        mock_repo = MagicMock()
        mock_repo.graph.degree.return_value = 0
        ranker = HybridRanker(mock_repo)

        results = [
            self._make_result("a", "authentication login user password jwt token", 0.9),
            self._make_result("b", "database sql query orm model migration", 0.5),
            self._make_result("c", "jwt authentication bearer token decode", 0.7),
        ]

        ranked = ranker.rank("jwt authentication", results)
        assert len(ranked) == 3
        # All results should have rrf_score in metadata
        for r in ranked:
            assert "rrf_score" in r.metadata
            assert r.metadata["rrf_score"] > 0

    def test_bm25_scores_relevant_chunk_higher(self):
        from app.retrieval.ranker import HybridRanker

        mock_repo = MagicMock()
        mock_repo.graph.degree.return_value = 0
        ranker = HybridRanker(mock_repo)

        relevant = self._make_result("rel", "implement jwt decode token bearer authentication", 0.6)
        irrelevant = self._make_result("irr", "css flexbox grid layout margin padding color", 0.6)

        ranked = ranker.rank("jwt token authentication", [relevant, irrelevant])
        # Relevant chunk should rank higher
        assert ranked[0].chunk.id == "rel"

    def test_empty_results_returns_empty(self):
        from app.retrieval.ranker import HybridRanker

        mock_repo = MagicMock()
        ranker = HybridRanker(mock_repo)
        assert ranker.rank("query", []) == []


# ---------------------------------------------------------------------------
# Phase 1: Diff Engine (existing, verify still works after refactor)
# ---------------------------------------------------------------------------


class TestLineDiffEngine:
    def test_apply_modify_patch(self):
        from app.coding.diff_engine import LineDiffEngine, StructuredPatch, LineHunk, EditType

        original = "line1\nline2\nline3\n"
        patch = StructuredPatch(
            file_path="test.py",
            edit_type=EditType.MODIFY,
            hunks=[
                LineHunk(
                    start_line=2,
                    end_line=2,
                    target_content="line2\n",
                    replacement_content="line2_modified\n",
                )
            ],
        )
        result = LineDiffEngine.apply_patch(original, patch)
        assert "line2_modified" in result
        assert "line1" in result
        assert "line3" in result

    def test_apply_create_patch(self):
        from app.coding.diff_engine import LineDiffEngine, StructuredPatch, EditType

        patch = StructuredPatch(
            file_path="new_file.py",
            edit_type=EditType.CREATE,
            full_content="print('hello world')\n",
        )
        result = LineDiffEngine.apply_patch("", patch)
        assert result == "print('hello world')\n"

    def test_generate_unified_diff(self):
        from app.coding.diff_engine import LineDiffEngine

        diff = LineDiffEngine.generate_unified_diff(
            "a\nb\nc\n",
            "a\nB\nc\n",
            file_path="test.py",
        )
        assert "---" in diff
        assert "+++" in diff
        assert "-b" in diff
        assert "+B" in diff


# ---------------------------------------------------------------------------
# Phase 4: SpecParser
# ---------------------------------------------------------------------------


class TestSpecParser:
    def test_discovers_agents_md(self, tmp_path):
        from app.parser.spec_parser import SpecParser, SPEC_FILENAMES

        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text(
            "# Architecture\n"
            "- Use async/await for all I/O operations\n"
            "- Never use global state\n"
            "\n# Style\n"
            "- Follow PEP 8\n"
            "\n# Test\n"
            "- pytest -v --tb=short\n"
            "\n# Prohibited\n"
            "- requests (use httpx)\n",
            encoding="utf-8",
        )

        spec = SpecParser.discover_and_parse(str(tmp_path))
        assert spec.has_spec is True
        assert spec.source_file == "AGENTS.md"
        assert any("async" in r for r in spec.architectural_rules)
        assert any("PEP" in g for g in spec.coding_style_guidelines)
        assert any("httpx" in p for p in spec.prohibited_packages)
        assert any("pytest" in c for c in spec.custom_test_commands)

    def test_returns_empty_spec_when_no_file(self, tmp_path):
        from app.parser.spec_parser import SpecParser

        spec = SpecParser.discover_and_parse(str(tmp_path))
        assert spec.has_spec is False


# ---------------------------------------------------------------------------
# Phase 6: MCPServerInfo model validation
# ---------------------------------------------------------------------------


class TestMCPModels:
    def test_http_server_info(self):
        from app.mcp.models import MCPServerInfo, MCPTransport

        server = MCPServerInfo(
            id="github-mcp",
            name="GitHub MCP",
            transport=MCPTransport.HTTP,
            url="https://api.example.com/mcp",
            api_key="sk-test-123",
        )
        assert server.url == "https://api.example.com/mcp"
        assert server.api_key == "sk-test-123"
        assert server.command is None

    def test_stdio_server_info(self):
        from app.mcp.models import MCPServerInfo, MCPTransport

        server = MCPServerInfo(
            id="local-mcp",
            name="Local MCP",
            transport=MCPTransport.STDIO,
            command=["npx", "@modelcontextprotocol/server-filesystem", "/tmp"],
        )
        assert server.command == ["npx", "@modelcontextprotocol/server-filesystem", "/tmp"]
        assert server.url is None

    def test_tool_registration(self):
        from app.mcp.models import MCPTool

        tool = MCPTool(
            name="create_pull_request",
            description="Create a GitHub PR",
            input_schema={"type": "object", "properties": {"title": {"type": "string"}}},
        )
        assert tool.name == "create_pull_request"

    def test_mcp_response_success(self):
        from app.mcp.models import MCPResponse

        resp = MCPResponse(success=True, result={"output": "done"})
        assert resp.success
        assert resp.error is None

    def test_mcp_response_failure(self):
        from app.mcp.models import MCPResponse

        resp = MCPResponse(success=False, error="Tool not found")
        assert not resp.success
        assert resp.error == "Tool not found"


# ---------------------------------------------------------------------------
# Phase 6: MCPClientManager tool registration
# ---------------------------------------------------------------------------


class TestMCPClientManager:
    def test_register_server(self):
        from app.mcp.mcp_client import MCPClientManager
        from app.mcp.models import MCPServerInfo, MCPTransport

        mgr = MCPClientManager()
        server = MCPServerInfo(
            id="test-srv",
            name="Test",
            transport=MCPTransport.HTTP,
            url="http://localhost:9000",
        )
        result = mgr.register_server(server)
        assert result is True
        assert "test-srv" in mgr.servers

    def test_register_tool_and_list(self):
        from app.mcp.mcp_client import MCPClientManager
        from app.mcp.models import MCPServerInfo, MCPTool, MCPTransport

        mgr = MCPClientManager()
        server = MCPServerInfo(
            id="srv1",
            name="Srv",
            transport=MCPTransport.HTTP,
            url="http://localhost:9000",
        )
        mgr.register_server(server)

        tool = MCPTool(
            name="search_code",
            description="Search codebase",
            input_schema={},
        )
        mgr.register_tool("srv1", tool)

        tools = mgr.list_available_tools()
        assert any(t.name == "search_code" for t in tools)

    @pytest.mark.asyncio
    async def test_execute_unregistered_tool_returns_error(self):
        from app.mcp.mcp_client import MCPClientManager

        mgr = MCPClientManager()
        response = await mgr.execute_tool("nonexistent_tool", {})
        assert response.success is False
        assert "not registered" in response.error
