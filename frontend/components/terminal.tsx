"use client";

import { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";

import "xterm/css/xterm.css";

export default function IDETerminal({
  sessionId,
  onResize,
}: {
  sessionId: string;
  onResize?: (cols: number, rows: number) => void;
}) {
  const divRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!divRef.current) return;

    const terminal = new Terminal({
      cursorBlink: true,
      convertEol: true,
      fontSize: 13,
      scrollback: 5000,
      theme: {
        background: "#111111",
      },
    });

    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);

    terminal.open(divRef.current);

    // xterm can't compute cell/font dimensions on a zero-size container.
    const safeFit = (socket?: WebSocket) => {
      const el = divRef.current;
      if (!el || el.offsetWidth === 0 || el.offsetHeight === 0) return;
      if (!terminal.element) return;
      try {
        fitAddon.fit();
        const { cols, rows } = terminal;
        onResize?.(cols, rows);
        // Tell backend PTY about new dimensions
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "resize", cols, rows }));
        }
      } catch (err) {
        console.warn("Terminal fit skipped:", err);
      }
    };

    const socket = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    socket.onopen = () => {
      setTimeout(() => {
        safeFit(socket);
        terminal.focus();
      }, 100);
    };

    socket.onmessage = (event) => {
      terminal.write(event.data);
    };

    socket.onerror = (err) => {
      console.error("WebSocket Error", err);
    };

    socket.onclose = () => {
      console.log("WebSocket closed");
    };

    terminal.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(data);
      }
    });

    requestAnimationFrame(() => {
      safeFit(socket);
      terminal.focus();
    });

    const focusHandler = () => terminal.focus();
    divRef.current.addEventListener("click", focusHandler);

    const resizeHandler = () => safeFit(socket);
    window.addEventListener("resize", resizeHandler);

    const observer = new ResizeObserver(() => {
      safeFit(socket);
    });

    observer.observe(divRef.current);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", resizeHandler);
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
    <div
      ref={divRef}
      className="w-full h-full overflow-hidden"
      tabIndex={0}
    />
  );
}