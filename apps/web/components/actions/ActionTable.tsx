"use client";

import { format } from "date-fns";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

interface ActionItem {
  id: string;
  description: string;
  owner_text: string | null;
  due_date: string | null;
  status: string;
  priority: string;
  meeting_title: string | null;
  meeting_id: string;
}

interface ActionTableProps {
  actions: ActionItem[];
  onStatusChange: (id: string, status: string) => void;
  onPriorityChange: (id: string, priority: string) => void;
}

const priorityVariant: Record<string, any> = {
  high: "red",
  medium: "yellow",
  low: "secondary",
};

const statusVariant: Record<string, any> = {
  todo: "secondary",
  doing: "blue",
  done: "green",
  blocked: "red",
};

export function ActionTable({ actions, onStatusChange, onPriorityChange }: ActionTableProps) {
  return (
    <div className="rounded-md border overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="text-left p-3 font-medium">Description</th>
            <th className="text-left p-3 font-medium">Meeting</th>
            <th className="text-left p-3 font-medium">Owner</th>
            <th className="text-left p-3 font-medium">Due Date</th>
            <th className="text-left p-3 font-medium">Priority</th>
            <th className="text-left p-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {actions.map((a) => (
            <tr key={a.id} className="border-b hover:bg-muted/30 transition-colors">
              <td className="p-3 max-w-xs">
                <p className="truncate">{a.description}</p>
              </td>
              <td className="p-3">
                {a.meeting_title && (
                  <Link
                    href={`/meetings/${a.meeting_id}`}
                    className="text-primary hover:underline text-xs truncate block max-w-[120px]"
                  >
                    {a.meeting_title}
                  </Link>
                )}
              </td>
              <td className="p-3 text-muted-foreground">{a.owner_text || "—"}</td>
              <td className="p-3 text-muted-foreground">
                {a.due_date ? format(new Date(a.due_date), "dd MMM yyyy") : "—"}
              </td>
              <td className="p-3">
                <select
                  value={a.priority}
                  onChange={(e) => onPriorityChange(a.id, e.target.value)}
                  className="text-xs rounded border border-input bg-background px-1.5 py-0.5"
                >
                  {["low", "medium", "high"].map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </td>
              <td className="p-3">
                <select
                  value={a.status}
                  onChange={(e) => onStatusChange(a.id, e.target.value)}
                  className="text-xs rounded border border-input bg-background px-1.5 py-0.5"
                >
                  {["todo", "doing", "done", "blocked"].map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
