"use client";

import ReactMarkdown from "react-markdown";

interface AIOutputProps {
  markdown: string;
}

export function AIOutput({ markdown }: AIOutputProps) {
  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown
        components={{
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold mb-4 text-foreground">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold mt-6 mb-3 text-foreground border-b pb-1">{children}</h2>
          ),
          ul: ({ children }) => (
            <ul className="list-disc list-inside space-y-1 text-sm text-foreground">{children}</ul>
          ),
          li: ({ children }) => (
            <li className="text-sm text-foreground">{children}</li>
          ),
          p: ({ children }) => (
            <p className="text-sm text-foreground mb-2">{children}</p>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border border-border px-3 py-2 text-left font-semibold bg-muted">{children}</th>
          ),
          td: ({ children }) => (
            <td className="border border-border px-3 py-2">{children}</td>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">{children}</strong>
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
