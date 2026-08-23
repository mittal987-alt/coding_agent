"use client";
import { wsBaseUrl } from "@/lib/api";

import { useEffect, useRef, useState } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import { WebLinksAddon } from "xterm-addon-web-links";

import "xterm/css/xterm.css";

export default function IDETerminal({
  sessionId,
  onSessionExpired,
  onReady,
  onFocus,
}: {
  sessionId: string;
  onSessionExpired?: () => void;
  /** Called once the terminal is mounted. Receives actions the parent can call. */
  onReady?: (actions: { clear: () => void; getContent: () => string }) => void;
  onFocus?: () => void;
}) {
  const divRef = useRef<HTMLDivElement>(null);
  const [expired, setExpired] = useState(false);

  useEffect(() => {
    if (!divRef.current) return;
    setExpired(false);

    const terminal = new Terminal({
      cursorBlink: true,
      // Do NOT set convertEol — the PTY (winpty) already sends \r\n.
      // Setting convertEol:true causes double line-feeds.
      convertEol: false,
      fontSize: 13,
      fontFamily: "'Cascadia Code', 'Fira Code', 'Consolas', monospace",
      scrollback: 5000,
      allowProposedApi: true,
      theme: {
        background: "#111111",
        foreground: "#d4d4d4",
        cursor: "#aeafad",
        cursorAccent: "#111111",
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

    requestAnimationFrame(() => {
      fitAddon.fit();
      terminal.focus();
    });

    // Expose actions to the parent via onReady
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

    const focusHandler = () => {
      terminal.focus();
      onFocus?.();
    };
    divRef.current.addEventListener("click", focusHandler);

   

    const socket = new WebSocket(`${wsBaseUrl}/ws/${sessionId}`);

    // Send the current terminal dimensions to the backend as soon as the
    // WebSocket opens so the PTY cols/rows match what xterm is rendering.
    const sendResize = (cols: number, rows: number) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: "resize", cols, rows }));
      }
    };

    socket.onopen = () => {
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
      console.log("WebSocket closed", event.code, event.reason);
      // 4001 = our custom "session_expired" close code from the backend
      if (event.code === 4001) {
        setExpired(true);
      }
    };

    terminal.onData((data) => {
      // Ctrl+L → clear the xterm viewport (the shell will also receive ^L
      // which clears the PowerShell host buffer on its side too).
      if (data === "\x0c") {
        terminal.clear();
      }
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(data);
      }
    });

    // Whenever xterm changes its cols/rows (due to fitAddon), tell the backend.
    terminal.onResize(({ cols, rows }) => {
      sendResize(cols, rows);
    });

    const handleWindowResize = () => {
      fitAddon.fit();
    };

    window.addEventListener("resize", handleWindowResize);

    const observer = new ResizeObserver(() => {
      // Debounce slightly so we don't flood resize messages while
      // the user is dragging a panel splitter.
      requestAnimationFrame(() => {
        fitAddon.fit();
      });
    });

    observer.observe(divRef.current);

    return () => {
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
  }, [sessionId]); // eslint-disable-line react-hooks/exhaustive-deps

  if (expired) {
    return (
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-[#111111] text-center px-6 z-10">
        <p className="text-sm text-gray-400">
          This terminal session expired (likely a backend restart).
        </p>
        {onSessionExpired ? (
          <button
            onClick={onSessionExpired}
            className="text-xs px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Start a new terminal
          </button>
        ) : (
          <p className="text-xs text-gray-600">
            (No reconnect handler was provided to this terminal.)
          </p>
        )}
      </div>
    );
  }

  return (
    <div
      ref={divRef}
      className="w-full h-full overflow-hidden"
      tabIndex={0}
    />
  );
}
