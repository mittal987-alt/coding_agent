"use client";

import { useEffect, useRef, useState } from "react";
import {
  Loader2,
  CheckCircle2,
  Brain,
  Code2,
  Search,
  FlaskConical,
  GitBranch,
  Database,
  Terminal,
  Globe,
  FileText,
  ChevronDown,
  ChevronUp,
  Zap,
  AlertCircle,
} from "lucide-react";

type ActivityStatus = "running" | "done" | "error";

type Activity = {
  text: string;
  timestamp: Date;
  status: ActivityStatus;
};

/* ─────────────── Agent-type detection ─────────────── */
function detectAgentType(text: string): {
  icon: React.ReactNode;
  color: string;
  agentName: string;
} {
  const t = text.toLowerCase();

  if (t.includes("plan") || t.includes("analyz") || t.includes("think") || t.includes("understand")) {
    return { icon: <Brain size={12} />, color: "text-purple-400", agentName: "Planner" };
  }
  if (t.includes("writ") || t.includes("creat") || t.includes("generat") || t.includes("cod") || t.includes("implement") || t.includes("edit") || t.includes("modif")) {
    return { icon: <Code2 size={12} />, color: "text-blue-400", agentName: "Coder" };
  }
  if (t.includes("test") || t.includes("validat") || t.includes("verif") || t.includes("assert") || t.includes("check")) {
    return { icon: <FlaskConical size={12} />, color: "text-green-400", agentName: "Tester" };
  }
  if (t.includes("review") || t.includes("inspect") || t.includes("audit") || t.includes("lint") || t.includes("quality")) {
    return { icon: <Search size={12} />, color: "text-yellow-400", agentName: "Reviewer" };
  }
  if (t.includes("git") || t.includes("commit") || t.includes("branch") || t.includes("merge") || t.includes("push")) {
    return { icon: <GitBranch size={12} />, color: "text-orange-400", agentName: "Git" };
  }
  if (t.includes("memor") || t.includes("recall") || t.includes("stor") || t.includes("retriev") || t.includes("context")) {
    return { icon: <Database size={12} />, color: "text-pink-400", agentName: "Memory" };
  }
  if (t.includes("terminal") || t.includes("run") || t.includes("execut") || t.includes("command") || t.includes("shell")) {
    return { icon: <Terminal size={12} />, color: "text-cyan-400", agentName: "Terminal" };
  }
  if (t.includes("search") || t.includes("web") || t.includes("fetch") || t.includes("http") || t.includes("api")) {
    return { icon: <Globe size={12} />, color: "text-teal-400", agentName: "Web" };
  }
  if (t.includes("file") || t.includes("read") || t.includes("write") || t.includes("path") || t.includes("director")) {
    return { icon: <FileText size={12} />, color: "text-indigo-400", agentName: "FileSystem" };
  }
  return { icon: <Zap size={12} />, color: "text-gray-400", agentName: "Agent" };
}

function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function ActivityRow({
  activity,
  isLast,
  index,
}: {
  activity: Activity;
  isLast: boolean;
  index: number;
}) {
  const { icon, color, agentName } = detectAgentType(activity.text);

  return (
    <div
      className="flex items-start gap-2 text-xs py-1 px-2 rounded-lg transition-all duration-300"
      style={{
        animation: `fadeSlideIn 0.2s ease forwards`,
        animationDelay: `${index * 0.03}s`,
        opacity: 0,
      }}
    >
      {/* Timeline dot + line */}
      <div className="flex flex-col items-center shrink-0 mt-0.5">
        <div
          className={`flex items-center justify-center w-5 h-5 rounded-full shrink-0 ${
            isLast
              ? "bg-blue-500/20 border border-blue-500/50"
              : "bg-gray-800 border border-gray-700"
          }`}
        >
          {isLast ? (
            <Loader2
              size={10}
              className="animate-spin text-blue-400"
            />
          ) : activity.status === "error" ? (
            <AlertCircle size={10} className="text-red-400" />
          ) : (
            <CheckCircle2 size={10} className="text-green-500/70" />
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 mb-0.5">
          <span className={`flex items-center gap-1 font-semibold ${color}`}>
            {icon}
            <span className="text-[10px] uppercase tracking-wider">{agentName}</span>
          </span>
          <span className="text-[10px] text-gray-600 font-mono">
            {formatTimestamp(activity.timestamp)}
          </span>
        </div>
        <p
          className={`leading-snug break-words ${
            isLast
              ? "text-blue-200 font-medium"
              : "text-gray-500"
          }`}
        >
          {activity.text}
        </p>
      </div>
    </div>
  );
}

export default function AgentActivityLog({
  activities,
}: {
  activities: string[];
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll when new activities arrive
  useEffect(() => {
    if (isExpanded) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [activities, isExpanded]);

  if (activities.length === 0) return null;

  // Convert raw strings to Activity objects with timestamps
  // We use index as a proxy for timing (in reality, timestamps arrive from SSE)
  const activityObjects: Activity[] = activities.map((text, i) => ({
    text,
    timestamp: new Date(Date.now() - (activities.length - 1 - i) * 800),
    status: i < activities.length - 1 ? "done" : "running",
  }));

  return (
    <div className="mt-2 rounded-xl border border-gray-700/50 bg-gray-900/60 backdrop-blur-sm overflow-hidden">
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Header */}
      <button
        onClick={() => setIsExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-800/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
            </span>
          </div>
          <span className="text-[11px] font-semibold text-gray-300 uppercase tracking-wider">
            Agent Activity
          </span>
          <span className="text-[10px] font-mono text-gray-600 bg-gray-800 px-1.5 py-0.5 rounded-full">
            {activities.length}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp size={12} className="text-gray-500" />
        ) : (
          <ChevronDown size={12} className="text-gray-500" />
        )}
      </button>

      {/* Activity list */}
      {isExpanded && (
        <div className="max-h-48 overflow-y-auto px-1 pb-2 space-y-0.5">
          {activityObjects.map((activity, i) => (
            <ActivityRow
              key={i}
              activity={activity}
              isLast={i === activityObjects.length - 1}
              index={i}
            />
          ))}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
