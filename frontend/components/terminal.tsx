"use client";

import { useEffect, useRef, useState } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { WebLinksAddon } from "xterm-addon-web-links";
import { Terminal as TerminalIcon, RotateCcw } from "lucide-react";

import "xterm/css/xterm.css";

export default function IDETerminal({
  sessionId,
  onSessionExpired,
  onReady,
}: {
  sessionId: string;
  onSessionExpired?: () => void;
  onReady?: (actions: { clear: () => void; getContent: () => string }) => void;
}) {
  const divRef = useRef<HTMLDivElement>(null);
  const [expired, setExpired] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!divRef.current) return;
    setExpired(false);

    const terminal = new Terminal({
      cursorBlink: true,
      convertEol: false,
      fontSize: 13,
      fontFamily: "'Cascadia Code', 'Fira Code', 'Consolas', monospace",
      scrollback: 5000,
      allowProposedApi: true,
      theme: {
        background: "#0d0d0d",
        foreground: "#d4d4d4",
        cursor: "#aeafad",
        cursorAccent: "#0d0d0d",
        selectionBackground: "#264f78",
        black: "#1e1e1e",
        red: "#f44747",
        green: "#6a9955",
        yellow: "#d7ba7d",
        blue: "#569cd6",
        magenta: "#c586c0",
        cyan: "#4ec9b0",
        white: "#d4d4d4",
        brightBlack: "#808080",
        brightRed: "#f44747",
        brightGreen: "#b5cea8",
        brightYellow: "#dcdcaa",
        brightBlue: "#9cdcfe",
        brightMagenta: "#c586c0",
        brightCyan: "#4ec9b0",
        brightWhite: "#ffffff",
      },
    });

    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(new WebLinksAddon());

    terminal.open(divRef.current);

    const timer = setTimeout(() => {
      fitAddon.fit();
      terminal.focus();
    }, 50);

    onReady?.({
      clear: () => terminal.clear(),
      getContent: () => {
        const buffer = terminal.buffer.active;
        let content = "";
        for (let i = 0; i < buffer.length; i++) {
          const line = buffer.getLine(i);
          if (line) {
            content += line.translateToString(true) + "\n";
          }
        }
        return content;
      }
    });

    const focusHandler = () => terminal.focus();
    divRef.current.addEventListener("click", focusHandler);

    const socket = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    const sendResize = (cols: number, rows: number) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "resize", cols, rows }));
      }
    };

    socket.onopen = () => {
      setIsConnected(true);
      setTimeout(() => {
        fitAddon.fit();
        sendResize(terminal.cols, terminal.rows);
        terminal.focus();
      }, 100);
    };

    socket.onmessage = (event) => {
      terminal.write(event.data);
    };

    socket.onerror = (err) => {
      console.error("WebSocket Error", err);
    };

    socket.onclose = (event) => {
      setIsConnected(false);
      if (event.code === 4001) {
        setExpired(true);
      }
    };

    terminal.onData((data) => {
      if (data === "\x0c") {
        terminal.clear();
      }
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(data);
      }
    });

    terminal.onResize(({ cols, rows }) => {
      sendResize(cols, rows);
    });

    const handleWindowResize = () => {
      fitAddon.fit();
    };

    window.addEventListener("resize", handleWindowResize);

    const observer = new ResizeObserver(() => {
      requestAnimationFrame(() => {
        fitAddon.fit();
      });
    });

    if (divRef.current) {
      observer.observe(divRef.current);
    }

    return () => {
      clearTimeout(timer);
      observer.disconnect();
      window.removeEventListener("resize", handleWindowResize);
      divRef.current?.removeEventListener("click", focusHandler);

      if (
        socket.readyState === WebSocket.OPEN ||
        socket.readyState === WebSocket.CONNECTING
      ) {
        socket.close();
      }

      terminal.dispose();
    };
  }, [sessionId]);

  return (
    <div className="w-full h-full flex flex-col bg-[#0d0d0d] border border-border-subtle rounded-xl overflow-hidden shadow-2xl">
      
      {/* Terminal Window Header Bar */}
      <div className="h-9 px-4 bg-surface-1 border-b border-border-subtle flex items-center justify-between select-none shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80 hover:bg-red-500 transition-colors cursor-pointer" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80 hover:bg-yellow-500 transition-colors cursor-pointer" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80 hover:bg-emerald-500 transition-colors cursor-pointer" />
          </div>
          <div className="h-3 w-[1px] bg-border-subtle" />
          <div className="flex items-center gap-2 text-xs font-mono text-text-secondary">
            <TerminalIcon size={13} className="text-accent" />
            <span>bash // pty-session</span>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-emerald-500 animate-pulse" : "bg-amber-500 animate-ping"}`} />
          <span className="text-text-muted">{isConnected ? "connected" : "connecting..."}</span>
        </div>
      </div>

      {/* Terminal Viewport Container (min-h-0 prevents flex collapse) */}
      <div className="relative flex-1 min-h-0 w-full overflow-hidden p-2 bg-[#0d0d0d]">
        {expired && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-[#0d0d0d]/95 backdrop-blur-sm text-center px-6 z-10">
            <p className="text-xs font-mono text-text-secondary">
              // session expired (backend runtime disconnected)
            </p>
            {onSessionExpired ? (
              <button
                onClick={onSessionExpired}
                className="flex items-center gap-2 text-xs font-mono px-4 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg transition-all shadow-md shadow-blue-500/20"
              >
                <RotateCcw size={13} />
                <span>Restart PTY Shell</span>
              </button>
            ) : null}
          </div>
        )}

        <div
          ref={divRef}
          className="w-full h-full overflow-hidden outline-none"
          tabIndex={0}
        />
      </div>

    </div>
  );
}