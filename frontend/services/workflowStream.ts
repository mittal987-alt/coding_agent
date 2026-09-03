/**
 * useWorkflowStream — React hook for live LangGraph execution state via SSE.
 *
 * Subscribes to the backend's GET /api/v1/stream/{workflowId} SSE endpoint
 * and keeps a reactive list of LangGraphNode states in sync with each
 * node_started / node_completed / node_failed / hitl_interrupt event.
 *
 * Usage:
 *   const { nodes, hitlPending, hitlNodeId, error, connected } =
 *     useWorkflowStream("workflow-abc123");
 */

"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { LangGraphNode, AgentNodeStatus } from "@/components/GraphVisualizer";

// ------------------------------------------------------------------
// SSE event types emitted by the backend
// ------------------------------------------------------------------

interface SSENodeStarted {
  type: "node_started";
  node_id: string;
  node_name: string;
  role: string;
}

interface SSENodeCompleted {
  type: "node_completed";
  node_id: string;
  details?: string;
}

interface SSENodeFailed {
  type: "node_failed";
  node_id: string;
  error: string;
}

interface SSEHitlInterrupt {
  type: "hitl_interrupt";
  node_id: string;
  node_name: string;
}

interface SSEWorkflowDone {
  type: "workflow_done";
  response?: string;
}

type SSEEvent =
  | SSENodeStarted
  | SSENodeCompleted
  | SSENodeFailed
  | SSEHitlInterrupt
  | SSEWorkflowDone;

// ------------------------------------------------------------------
// Default agent node definitions (used as fallback before SSE data arrives)
// ------------------------------------------------------------------

const DEFAULT_PIPELINE_NODES: LangGraphNode[] = [
  { id: "supervisor",  name: "Supervisor",  role: "Routing & Orchestration",    status: "idle" },
  { id: "planner",     name: "Planner",     role: "Task Decomposition",         status: "idle" },
  { id: "repository",  name: "Repository",  role: "AST Indexing",               status: "idle" },
  { id: "retriever",   name: "Retriever",   role: "Hybrid RAG Retrieval",       status: "idle" },
  { id: "coder",       name: "Coder",       role: "Code Patch Generation",      status: "idle" },
  { id: "reviewer",    name: "Reviewer",    role: "Code Review",                status: "idle" },
  { id: "terminal",    name: "Terminal",    role: "Shell Execution",            status: "idle" },
  { id: "tester",      name: "Tester",      role: "Unit Test Runner",           status: "idle" },
  { id: "evaluator",   name: "Evaluator",   role: "TDD Self-Correction Loop",   status: "idle" },
  { id: "git",         name: "Git",         role: "Version Control",            status: "idle" },
  { id: "memory",      name: "Memory",      role: "Episodic Memory Storage",    status: "idle" },
  { id: "responder",   name: "Responder",   role: "Final Response Generation",  status: "idle" },
];

// ------------------------------------------------------------------
// Hook return type
// ------------------------------------------------------------------

export interface WorkflowStreamState {
  /** Reactive list of pipeline nodes with live status */
  nodes: LangGraphNode[];
  /** True when a HITL interrupt checkpoint is awaiting human approval */
  hitlPending: boolean;
  /** The node_id of the interrupted HITL node */
  hitlNodeId: string | null;
  /** Final workflow response text (set on workflow_done) */
  workflowResponse: string | null;
  /** SSE connection error message if connection failed */
  error: string | null;
  /** True while the EventSource connection is open */
  connected: boolean;
  /** Manually close the SSE stream */
  disconnect: () => void;
  /** Reset all nodes back to idle status */
  reset: () => void;
}

// ------------------------------------------------------------------
// Hook implementation
// ------------------------------------------------------------------

export function useWorkflowStream(
  workflowId: string | null,
  apiBase: string = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080/api/v1"
): WorkflowStreamState {
  const [nodes, setNodes] = useState<LangGraphNode[]>(DEFAULT_PIPELINE_NODES);
  const [hitlPending, setHitlPending] = useState(false);
  const [hitlNodeId, setHitlNodeId] = useState<string | null>(null);
  const [workflowResponse, setWorkflowResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  const eventSourceRef = useRef<EventSource | null>(null);

  // ------------------------------------------------------------------
  // Node state updater helper
  // ------------------------------------------------------------------

  const updateNodeStatus = useCallback(
    (nodeId: string, status: AgentNodeStatus, patch?: Partial<LangGraphNode>) => {
      setNodes((prev) =>
        prev.map((n) =>
          n.id === nodeId ? { ...n, status, ...patch } : n
        )
      );
    },
    []
  );

  // ------------------------------------------------------------------
  // SSE event dispatcher
  // ------------------------------------------------------------------

  const handleEvent = useCallback(
    (rawData: string) => {
      let event: SSEEvent;
      try {
        event = JSON.parse(rawData);
      } catch {
        return; // ignore malformed events
      }

      switch (event.type) {
        case "node_started":
          updateNodeStatus(event.node_id, "running", {
            name: event.node_name,
            role: event.role,
          });
          break;

        case "node_completed":
          updateNodeStatus(event.node_id, "completed", {
            details: event.details,
          });
          break;

        case "node_failed":
          updateNodeStatus(event.node_id, "failed", {
            details: event.error,
          });
          break;

        case "hitl_interrupt":
          updateNodeStatus(event.node_id, "interrupted");
          setHitlPending(true);
          setHitlNodeId(event.node_id);
          break;

        case "workflow_done":
          setWorkflowResponse(event.response ?? null);
          setConnected(false);
          eventSourceRef.current?.close();
          break;

        default:
          break;
      }
    },
    [updateNodeStatus]
  );

  // ------------------------------------------------------------------
  // Connect / disconnect lifecycle
  // ------------------------------------------------------------------

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setConnected(false);
  }, []);

  const reset = useCallback(() => {
    setNodes(DEFAULT_PIPELINE_NODES);
    setHitlPending(false);
    setHitlNodeId(null);
    setWorkflowResponse(null);
    setError(null);
  }, []);

  useEffect(() => {
    if (!workflowId) return;

    // Clean up any previous connection
    disconnect();
    reset();

    const url = `${apiBase}/stream/${encodeURIComponent(workflowId)}`;

    try {
      const es = new EventSource(url, { withCredentials: false });
      eventSourceRef.current = es;

      es.onopen = () => {
        setConnected(true);
        setError(null);
      };

      es.onmessage = (ev) => {
        handleEvent(ev.data);
      };

      // Named event listeners for semantic SSE channels
      es.addEventListener("node_started",    (ev) => handleEvent(ev.data));
      es.addEventListener("node_completed",   (ev) => handleEvent(ev.data));
      es.addEventListener("node_failed",      (ev) => handleEvent(ev.data));
      es.addEventListener("hitl_interrupt",   (ev) => handleEvent(ev.data));
      es.addEventListener("workflow_done",    (ev) => handleEvent(ev.data));

      es.onerror = () => {
        setError("SSE connection lost. Reconnecting…");
        setConnected(false);
      };
    } catch (err) {
      setError(String(err));
    }

    return () => {
      disconnect();
    };
  }, [workflowId, apiBase, handleEvent, disconnect, reset]);

  return {
    nodes,
    hitlPending,
    hitlNodeId,
    workflowResponse,
    error,
    connected,
    disconnect,
    reset,
  };
}

// ------------------------------------------------------------------
// HITL Approval helper
// ------------------------------------------------------------------

/**
 * Send an approve or reject action to the HITL REST API.
 *
 * @param workflowId  The workflow to approve/reject.
 * @param action      "approve" | "reject"
 * @param comment     Optional human comment (for approve) or reason (for reject).
 * @param apiBase     Backend API base URL.
 */
export async function sendHitlAction(
  workflowId: string,
  action: "approve" | "reject",
  comment: string = "",
  apiBase: string = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080/api/v1"
): Promise<{ success: boolean; message: string }> {
  const body =
    action === "approve"
      ? { comment }
      : { reason: comment || "Rejected by operator." };

  const resp = await fetch(
    `${apiBase}/hitl/${encodeURIComponent(workflowId)}/${action}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }
  );

  if (!resp.ok) {
    const err = await resp.text();
    return { success: false, message: err };
  }

  const data = await resp.json();
  return { success: data.success, message: data.message };
}
