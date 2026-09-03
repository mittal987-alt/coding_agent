"use client";

/**
 * GraphVisualizer — Live LangGraph execution pipeline visualizer.
 *
 * Subscribes to the backend SSE stream for the active workflow and
 * animates node status transitions in real time:
 *   idle → running → completed | failed | interrupted
 *
 * When a HITL interrupt fires, an approval dialog is shown inline.
 * The operator can approve (resume) or reject (abort) via the HITL REST API.
 */

import React, { useState } from "react";
import {
  Play,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Layers,
  ShieldAlert,
  Wifi,
  WifiOff,
  RotateCcw,
} from "lucide-react";
import { useWorkflowStream, sendHitlAction } from "@/services/workflowStream";

// ------------------------------------------------------------------
// Types (re-exported for consumers)
// ------------------------------------------------------------------

export type AgentNodeStatus = "idle" | "running" | "completed" | "failed" | "interrupted";

export interface LangGraphNode {
  id: string;
  name: string;
  role: string;
  status: AgentNodeStatus;
  details?: string;
}

// ------------------------------------------------------------------
// Props
// ------------------------------------------------------------------

interface GraphVisualizerProps {
  /**
   * Active workflow ID to subscribe to.
   * When null/undefined the visualizer shows the static idle pipeline.
   */
  workflowId?: string | null;
  /**
   * Static node overrides — used in Storybook / testing without a live stream.
   * Ignored when workflowId is provided.
   */
  staticNodes?: LangGraphNode[];
  /** Called after a successful HITL approve or reject action. */
  onHitlAction?: (workflowId: string, action: "approve" | "reject") => void;
}

// ------------------------------------------------------------------
// Status helpers
// ------------------------------------------------------------------

function NodeStatusIcon({ status }: { status: AgentNodeStatus }) {
  switch (status) {
    case "running":
      return <RefreshCw className="animate-spin text-blue-400" size={13} />;
    case "completed":
      return <CheckCircle2 className="text-green-400" size={13} />;
    case "interrupted":
      return <ShieldAlert className="text-amber-400" size={13} />;
    case "failed":
      return <AlertCircle className="text-red-400" size={13} />;
    default:
      return <Play className="text-gray-600" size={12} />;
  }
}

function nodeCardClass(status: AgentNodeStatus): string {
  const base =
    "relative flex flex-col p-3 rounded-lg border transition-all duration-300 ";
  switch (status) {
    case "running":
      return (
        base +
        "bg-blue-950/50 border-blue-500/80 shadow-lg shadow-blue-950/50 " +
        "text-blue-100 ring-1 ring-blue-400/50"
      );
    case "completed":
      return base + "bg-green-950/20 border-green-800/40 text-green-300";
    case "failed":
      return base + "bg-red-950/30 border-red-800/40 text-red-300";
    case "interrupted":
      return base + "bg-amber-950/40 border-amber-500/60 text-amber-200";
    default:
      return base + "bg-gray-900/60 border-gray-800 text-gray-400";
  }
}

// ------------------------------------------------------------------
// HITL Approval Dialog (inline)
// ------------------------------------------------------------------

interface HitlDialogProps {
  workflowId: string;
  nodeId: string;
  onComplete: (action: "approve" | "reject") => void;
}

function HitlApprovalDialog({ workflowId, nodeId, onComplete }: HitlDialogProps) {
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState<"approve" | "reject" | null>(null);
  const [result, setResult] = useState<string | null>(null);

  async function handleAction(action: "approve" | "reject") {
    setLoading(action);
    const res = await sendHitlAction(workflowId, action, comment);
    setResult(res.message);
    setLoading(null);
    if (res.success) {
      setTimeout(() => onComplete(action), 800);
    }
  }

  return (
    <div className="mt-3 p-3 rounded-lg bg-amber-950/60 border border-amber-600/50 text-xs text-amber-100 space-y-2">
      <p className="font-semibold flex items-center gap-1.5">
        <ShieldAlert size={12} />
        HITL Approval Required — node: <code className="font-mono">{nodeId}</code>
      </p>
      <p className="text-amber-300/80">
        The agent wants to execute a potentially destructive operation.
        Review the planned action before proceeding.
      </p>
      <textarea
        className="w-full text-[11px] bg-black/30 border border-amber-700/40 rounded p-1.5
                   text-amber-100 placeholder-amber-600/60 resize-none focus:outline-none"
        rows={2}
        placeholder="Optional comment / review note…"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      {result && (
        <p className="text-green-400 text-[11px]">{result}</p>
      )}
      <div className="flex gap-2">
        <button
          id={`hitl-approve-${workflowId}`}
          disabled={loading !== null}
          onClick={() => handleAction("approve")}
          className="flex-1 py-1 rounded text-[11px] font-semibold bg-green-600 hover:bg-green-500
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all text-white"
        >
          {loading === "approve" ? "Approving…" : "✓ Approve & Resume"}
        </button>
        <button
          id={`hitl-reject-${workflowId}`}
          disabled={loading !== null}
          onClick={() => handleAction("reject")}
          className="flex-1 py-1 rounded text-[11px] font-semibold bg-red-700 hover:bg-red-600
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all text-white"
        >
          {loading === "reject" ? "Rejecting…" : "✗ Reject & Abort"}
        </button>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------
// Main component
// ------------------------------------------------------------------

export default function GraphVisualizer({
  workflowId,
  staticNodes,
  onHitlAction,
}: GraphVisualizerProps) {
  const {
    nodes: liveNodes,
    hitlPending,
    hitlNodeId,
    error,
    connected,
    reset,
  } = useWorkflowStream(workflowId ?? null);

  // Use live nodes when a workflowId is provided, otherwise static fallback
  const nodes = workflowId ? liveNodes : (staticNodes ?? liveNodes);

  function handleHitlComplete(action: "approve" | "reject") {
    reset();
    if (workflowId) onHitlAction?.(workflowId, action);
  }

  return (
    <div className="flex flex-col bg-[#141414] border border-gray-800 rounded-xl p-4 shadow-xl text-gray-200 w-full gap-4">

      {/* ── Header ── */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Layers className="text-blue-400" size={18} />
          <h3 className="text-sm font-semibold tracking-wide text-gray-100">
            LangGraph Execution Pipeline
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {/* Connection indicator */}
          {workflowId && (
            <span
              className={`flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full border font-medium ${
                connected
                  ? "bg-green-950/50 border-green-700/50 text-green-400"
                  : error
                  ? "bg-red-950/40 border-red-700/40 text-red-400"
                  : "bg-gray-900 border-gray-700 text-gray-500"
              }`}
            >
              {connected ? (
                <><Wifi size={10} /> Live</>
              ) : error ? (
                <><WifiOff size={10} /> Disconnected</>
              ) : (
                <><WifiOff size={10} /> Idle</>
              )}
            </span>
          )}

          {/* Static badge when no workflowId */}
          {!workflowId && (
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-950/60 border border-blue-800/40 text-blue-400 font-medium">
              Live SSE Stream
            </span>
          )}

          {/* Reset button */}
          <button
            id="graph-reset-btn"
            onClick={reset}
            title="Reset pipeline to idle"
            className="p-1 rounded hover:bg-gray-800 text-gray-500 hover:text-gray-300 transition-all"
          >
            <RotateCcw size={13} />
          </button>
        </div>
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div className="text-xs text-red-400 bg-red-950/30 border border-red-800/40 rounded px-3 py-2">
          {error}
        </div>
      )}

      {/* ── HITL approval dialog ── */}
      {hitlPending && hitlNodeId && workflowId && (
        <HitlApprovalDialog
          workflowId={workflowId}
          nodeId={hitlNodeId}
          onComplete={handleHitlComplete}
        />
      )}

      {/* ── Pipeline nodes grid ── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {nodes.map((node) => (
          <div key={node.id} className={nodeCardClass(node.status)}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-bold truncate">{node.name}</span>
              <NodeStatusIcon status={node.status} />
            </div>
            <span className="text-[11px] text-gray-400 truncate">{node.role}</span>
            {node.details && (
              <span className="mt-1 text-[10px] text-gray-500 line-clamp-2 leading-tight">
                {node.details}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
