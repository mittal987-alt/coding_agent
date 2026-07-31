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
      fontSize: 13,
      convertEol: true,
      scrollback: 5000,
      theme: {
        background: "#111111",
      },
    });

    const fitAddon = new FitAddon();

    terminal.loadAddon(fitAddon);

    terminal.open(divRef.current);

    // Wait for layout
    requestAnimationFrame(() => {
      fitAddon.fit();
    });

    const socket = new WebSocket(
      `ws://localhost:8000/ws/${sessionId}`
    );

    socket.onopen = () => {
      setTimeout(() => {
        fitAddon.fit();
      }, 50);
    };

    socket.onmessage = (event) => {
      terminal.write(event.data);
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
      socket.close();
      terminal.dispose();
    };
  }, [sessionId]);

  return (
    <div
      ref={divRef}
      className="w-full h-full overflow-hidden"
    />
  );
}