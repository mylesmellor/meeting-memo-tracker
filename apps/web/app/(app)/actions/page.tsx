"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ActionTable } from "@/components/actions/ActionTable";
import { KanbanBoard } from "@/components/actions/KanbanBoard";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { LayoutGrid, Table2, AlertTriangle, Clock } from "lucide-react";

interface ActionItem {
  id: string;
  description: string;
  owner_text: string | null;
  due_date: string | null;
  status: string;
  priority: string;
  meeting_title: string | null;
  meeting_id: string;
  meeting_category: string | null;
}

export default function ActionsPage() {
  const [view, setView] = useState<"table" | "kanban">("table");
  const [filterStatus, setFilterStatus] = useState("");
  const [filterPriority, setFilterPriority] = useState("");
  const [overdue, setOverdue] = useState(false);
  const [dueThisWeek, setDueThisWeek] = useState(false);

  const qc = useQueryClient();

  const buildParams = () => {
    const p = new URLSearchParams();
    if (filterStatus) p.set("status", filterStatus);
    if (filterPriority) p.set("priority", filterPriority);
    if (overdue) p.set("overdue", "true");
    if (dueThisWeek) p.set("due_this_week", "true");
    p.set("limit", "100");
    return p.toString();
  };

  const { data, isLoading } = useQuery({
    queryKey: ["actions", filterStatus, filterPriority, overdue, dueThisWeek],
    queryFn: () =>
      apiFetch<{ items: ActionItem[]; total: number }>(`/api/v1/actions/?${buildParams()}`),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, patch }: { id: string; patch: any }) =>
      apiFetch(`/api/v1/actions/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["actions"] }),
    onError: (e: any) => toast.error(e.message),
  });

  const handleStatusChange = (id: string, status: string) => {
    updateMutation.mutate({ id, patch: { status } });
  };

  const handlePriorityChange = (id: string, priority: string) => {
    updateMutation.mutate({ id, patch: { priority } });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Action Board</h1>
          <p className="text-muted-foreground">
            {data?.total ?? 0} action{data?.total !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex gap-1 border rounded-md p-1">
          <button
            onClick={() => setView("table")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition-colors ${
              view === "table" ? "bg-primary text-primary-foreground" : "hover:bg-accent"
            }`}
          >
            <Table2 className="h-4 w-4" />
            Table
          </button>
          <button
            onClick={() => setView("kanban")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition-colors ${
              view === "kanban" ? "bg-primary text-primary-foreground" : "hover:bg-accent"
            }`}
          >
            <LayoutGrid className="h-4 w-4" />
            Kanban
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 items-center">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="text-sm rounded-md border border-input bg-background px-3 py-1.5"
        >
          <option value="">All statuses</option>
          {["todo", "doing", "done", "blocked"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
          className="text-sm rounded-md border border-input bg-background px-3 py-1.5"
        >
          <option value="">All priorities</option>
          {["low", "medium", "high"].map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>

        <button
          onClick={() => { setOverdue(!overdue); if (!overdue) setDueThisWeek(false); }}
          className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm transition-colors ${
            overdue ? "border-red-500 bg-red-50 text-red-700" : "border-input hover:bg-accent"
          }`}
        >
          <AlertTriangle className="h-3 w-3" />
          Overdue
        </button>

        <button
          onClick={() => { setDueThisWeek(!dueThisWeek); if (!dueThisWeek) setOverdue(false); }}
          className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm transition-colors ${
            dueThisWeek ? "border-blue-500 bg-blue-50 text-blue-700" : "border-input hover:bg-accent"
          }`}
        >
          <Clock className="h-3 w-3" />
          Due this week
        </button>

        {(filterStatus || filterPriority || overdue || dueThisWeek) && (
          <button
            onClick={() => {
              setFilterStatus("");
              setFilterPriority("");
              setOverdue(false);
              setDueThisWeek(false);
            }}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Clear filters
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
        </div>
      ) : !data?.items.length ? (
        <div className="text-center py-16 text-muted-foreground">
          No action items found
        </div>
      ) : view === "table" ? (
        <ActionTable
          actions={data.items}
          onStatusChange={handleStatusChange}
          onPriorityChange={handlePriorityChange}
        />
      ) : (
        <KanbanBoard actions={data.items} onStatusChange={handleStatusChange} />
      )}
    </div>
  );
}
