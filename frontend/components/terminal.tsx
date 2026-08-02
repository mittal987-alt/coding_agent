"use client";

import { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";

import "xterm/css/xterm.css";

export default function IDETerminal({
  sessionId,
}: {
  sessionId: string;
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

    requestAnimationFrame(() => {
      fitAddon.fit();
      terminal.focus();
    });

    const focusHandler = () => terminal.focus();
    divRef.current.addEventListener("click", focusHandler);

    const socket = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    socket.onopen = () => {
      setTimeout(() => {
        fitAddon.fit();
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

    const resize = () => {
      fitAddon.fit();
    };

    window.addEventListener("resize", resize);

    const observer = new ResizeObserver(() => {
      fitAddon.fit();
    });

    observer.observe(divRef.current);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", resize);
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