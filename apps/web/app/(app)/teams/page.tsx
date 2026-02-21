"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ChevronRight, Trash2, Plus } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { toast } from "sonner";

interface User {
  id: string;
  role: string;
}

interface Team {
  id: string;
  name: string;
  slug: string;
}

export default function TeamsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<Team | null>(null);

  const { data: user } = useQuery<User>({
    queryKey: ["me"],
    queryFn: () => apiFetch<User>("/api/v1/auth/me"),
  });

  const { data: teams, isLoading } = useQuery<Team[]>({
    queryKey: ["teams"],
    queryFn: () => apiFetch<Team[]>("/api/v1/teams/"),
  });

  const isAdmin =
    user?.role === "org_admin" || user?.role === "team_admin";
  const isOrgAdmin = user?.role === "org_admin";

  const createMutation = useMutation({
    mutationFn: (name: string) =>
      apiFetch("/api/v1/teams/", { method: "POST", body: JSON.stringify({ name }) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teams"] });
      setCreateOpen(false);
      setNewName("");
      toast.success("Team created");
    },
    onError: () => toast.error("Failed to create team"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      apiFetch(`/api/v1/teams/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teams"] });
      setDeleteTarget(null);
      toast.success("Team deleted");
    },
    onError: () => toast.error("Failed to delete team"),
  });

  const handleCreate = () => {
    const name = newName.trim();
    if (!name) return;
    createMutation.mutate(name);
  };

  const filtered = (teams ?? []).filter((t) =>
    t.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Teams</h1>
          {teams && (
            <p className="text-sm text-muted-foreground">
              {teams.length} team{teams.length !== 1 ? "s" : ""}
            </p>
          )}
        </div>
        {isAdmin && (
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Team
          </Button>
        )}
      </div>

      {/* Search */}
      <Input
        placeholder="Search teams…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {/* Team cards */}
      {isLoading ? (
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-16 w-full rounded-lg" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
          {search ? (
            <p>No teams match &ldquo;{search}&rdquo;</p>
          ) : isAdmin ? (
            <p>
              No teams yet.{" "}
              <button
                className="underline hover:text-foreground transition-colors"
                onClick={() => setCreateOpen(true)}
              >
                Create your first team
              </button>
            </p>
          ) : (
            <p>No teams in your organisation yet.</p>
          )}
        </div>
      ) : (
        <ul className="space-y-2">
          {filtered.map((team) => (
            <li
              key={team.id}
              className="flex items-center rounded-lg border bg-card transition-colors hover:bg-accent/50"
            >
              <Link
                href={`/teams/${team.id}`}
                className="flex flex-1 items-center gap-3 px-4 py-3"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{team.name}</p>
                  <p className="text-xs text-muted-foreground">/{team.slug}</p>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
              </Link>
              {isOrgAdmin && (
                <button
                  onClick={() => setDeleteTarget(team)}
                  className="px-3 py-3 text-muted-foreground hover:text-destructive transition-colors"
                  aria-label="Delete team"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* Create Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Team</DialogTitle>
            <DialogDescription>Give your new team a name.</DialogDescription>
          </DialogHeader>
          <Input
            placeholder="Team name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            autoFocus
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={!newName.trim() || createMutation.isPending}
            >
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Team</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete{" "}
              <strong>{deleteTarget?.name}</strong>? This cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
              disabled={deleteMutation.isPending}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
