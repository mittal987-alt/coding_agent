"use client";

import { useState } from "react";
import { RefreshCw, ExternalLink } from "lucide-react";

export default function PreviewPanel({ defaultPort = 3000 }: { defaultPort?: number }) {
  const [port, setPort] = useState(defaultPort.toString());
  const [url, setUrl] = useState(`http://localhost:${defaultPort}`);
  const [key, setKey] = useState(0);

  const handleGo = () => {
    setUrl(`http://localhost:${port}`);
  };

  const handleRefresh = () => {
    setKey((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col h-full bg-white relative">
      <div className="absolute top-0 left-0 right-0 h-10 bg-gray-900 border-b border-gray-800 flex items-center px-4 gap-3 shrink-0 shadow-sm z-10">
        <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Preview</span>
        <div className="flex items-center gap-1.5 flex-1 max-w-sm mx-auto">
          <span className="text-xs text-gray-500">http://localhost:</span>
          <input
            type="number"
            value={port}
            onChange={(e) => setPort(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleGo();
            }}
            className="w-16 bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-gray-200 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleGo}
            className="px-2 py-1 bg-blue-600 hover:bg-blue-500 text-white text-xs rounded transition-colors font-medium"
          >
            Go
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
            title="Refresh preview"
          >
            <RefreshCw size={14} />
          </button>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
            title="Open in new tab"
          >
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
      
      <div className="flex-1 mt-10 bg-white">
        <iframe
          key={key}
          src={url}
          className="w-full h-full border-0"
          title="Preview"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
        />
      </div>
    </div>
  );
}
