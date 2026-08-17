import React, { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

export const CodeBlock = ({ node, className, children, ...props }: any) => {
  const [showPreview, setShowPreview] = useState(false);
  const match = /language-(\w+)/.exec(className || "");
  const isInline = !className && !String(children).includes("\n");
  const lang = match ? match[1] : "";
  const isPreviewable = lang === "html" || lang.includes("html");

  if (isInline || !match) {
    return <code className={`px-1 py-0.5 rounded-md bg-gray-200 dark:bg-gray-700 ${className || ""}`} {...props}>{children}</code>;
  }

  return (
    <div className="mt-2 mb-2 rounded-md overflow-hidden border border-gray-700 shadow-sm">
      <div className="bg-gray-800 text-gray-400 text-xs px-3 py-1 flex justify-between items-center h-8">
        <span className="font-mono uppercase text-[10px] tracking-wider">{lang}</span>
        {isPreviewable && (
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="flex items-center gap-1 hover:text-white transition-colors px-2 py-0.5 rounded bg-gray-700/50 hover:bg-gray-600"
          >
            {showPreview ? (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                Code
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                Preview
              </>
            )}
          </button>
        )}
      </div>
      {showPreview && isPreviewable ? (
        <div className="bg-white w-full h-[350px] relative">
          <iframe 
            sandbox="allow-scripts allow-modals allow-forms allow-popups"
            srcDoc={String(children)}
            className="absolute inset-0 w-full h-full border-none"
            title="Live Preview"
          />
        </div>
      ) : (
        <SyntaxHighlighter
          style={vscDarkPlus as any}
          language={lang}
          PreTag="div"
          customStyle={{ margin: 0, borderRadius: 0 }}
          {...props}
        >
          {String(children).replace(/\n$/, "")}
        </SyntaxHighlighter>
      )}
    </div>
  );
};
