"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Edit3,
  Check,
  X,
  UserMinus,
  UserPlus,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { toast } from "sonner";

interface CurrentUser {
  id: string;
  role: string;
}

interface Team {
  id: string;
  name: string;
  slug: string;
}

interface Member {
  id: string;
  name: string;
  email: string;
  role: string;
}

function roleBadgeVariant(role: string): "purple" | "blue" | "secondary" {
  if (role === "org_admin") return "purple";
  if (role === "team_admin") return "blue";
  return "secondary";
}

export default function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();

  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState("");
  const [selectedUserId, setSelectedUserId] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data: user } = useQuery<CurrentUser>({
    queryKey: ["me"],
    queryFn: () => apiFetch<CurrentUser>("/api/v1/auth/me"),
  });

  const { data: team, isLoading: teamLoading } = useQuery<Team>({
    queryKey: ["team", id],
    queryFn: () => apiFetch<Team>(`/api/v1/teams/${id}`),
    enabled: !!id,
  });

  const { data: members, isLoading: membersLoading } = useQuery<Member[]>({
    queryKey: ["team-members", id],
    queryFn: () => apiFetch<Member[]>(`/api/v1/teams/${id}/members`),
    enabled: !!id,
  });

  const isAdmin =
    user?.role === "org_admin" || user?.role === "team_admin";
  const isOrgAdmin = user?.role === "org_admin";

  const { data: orgUsers } = useQuery<Member[]>({
    queryKey: ["org-users"],
    queryFn: () => apiFetch<Member[]>("/api/v1/auth/users/"),
    enabled: isAdmin,
  });

  const memberIds = new Set((members ?? []).map((m) => m.id));
  const availableUsers = (orgUsers ?? []).filter((u) => !memberIds.has(u.id));

  const updateNameMutation = useMutation({
    mutationFn: (name: string) =>
      apiFetch(`/api/v1/teams/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ name }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["team", id] });
      qc.invalidateQueries({ queryKey: ["teams"] });
      setEditingName(false);
      toast.success("Team renamed");
    },
    onError: () => toast.error("Failed to rename team"),
  });

  const addMemberMutation = useMutation({
    mutationFn: (userId: string) =>
      apiFetch(`/api/v1/teams/${id}/members/${userId}`, { method: "POST" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["team-members", id] });
      setSelectedUserId("");
      toast.success("Member added");
    },
    onError: () => toast.error("Failed to add member"),
  });

  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) =>
      apiFetch(`/api/v1/teams/${id}/members/${userId}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["team-members", id] });
      toast.success("Member removed");
    },
    onError: () => toast.error("Failed to remove member"),
  });

  const deleteTeamMutation = useMutation({
    mutationFn: () =>
      apiFetch(`/api/v1/teams/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teams"] });
      router.push("/teams");
    },
    onError: () => toast.error("Failed to delete team"),
  });

  const startEditing = () => {
    setNameInput(team?.name ?? "");
    setEditingName(true);
  };

  const saveName = () => {
    const name = nameInput.trim();
    if (!name || name === team?.name) {
      setEditingName(false);
      return;
    }
    updateNameMutation.mutate(name);
  };

  const cancelEdit = () => setEditingName(false);

  if (teamLoading || membersLoading) {
    return (
      <div className="max-w-2xl space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48 w-full rounded-lg" />
      </div>
    );
  }

  if (!team) {
    return (
      <div className="max-w-2xl">
        <p className="text-muted-foreground">Team not found.</p>
        <Link href="/teams" className="text-sm underline hover:text-primary">
          Back to Teams
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/teams">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>

        {editingName ? (
          <div className="flex flex-1 items-center gap-2">
            <Input
              value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") saveName();
                if (e.key === "Escape") cancelEdit();
              }}
              autoFocus
              className="text-lg font-semibold"
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={saveName}
              disabled={updateNameMutation.isPending}
            >
              <Check className="h-4 w-4 text-green-600" />
            </Button>
            <Button variant="ghost" size="icon" onClick={cancelEdit}>
              <X className="h-4 w-4 text-muted-foreground" />
            </Button>
          </div>
        ) : (
          <div className="flex flex-1 items-center gap-2">
            <div>
              <h1 className="text-2xl font-bold leading-tight">{team.name}</h1>
              <p className="text-xs text-muted-foreground">/{team.slug}</p>
            </div>
            {isAdmin && (
              <Button
                variant="ghost"
                size="icon"
                onClick={startEditing}
                className="ml-1"
              >
                <Edit3 className="h-4 w-4 text-muted-foreground" />
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Members Card */}
      <Card>
        <CardHeader>
          <CardTitle>Members ({members?.length ?? 0})</CardTitle>
        </CardHeader>
        <CardContent className="space-y-0 p-0">
          {!members || members.length === 0 ? (
            <p className="px-6 pb-4 text-sm text-muted-foreground">
              No members yet.
            </p>
          ) : (
            <ul>
              {members.map((m, i) => (
                <li
                  key={m.id}
                  className={`flex items-center gap-3 px-6 py-3 ${
                    i < members.length - 1 ? "border-b" : ""
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{m.name}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {m.email}
                    </p>
                  </div>
                  <Badge variant={roleBadgeVariant(m.role)}>
                    {m.role.replace("_", " ")}
                  </Badge>
                  {isAdmin && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeMemberMutation.mutate(m.id)}
                      disabled={removeMemberMutation.isPending}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <UserMinus className="h-4 w-4" />
                    </Button>
                  )}
                </li>
              ))}
            </ul>
          )}

          {isAdmin && availableUsers.length > 0 && (
            <div className="flex items-center gap-2 border-t px-6 py-3">
              <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                <SelectTrigger className="flex-1">
                  <SelectValue placeholder="Select a user to add…" />
                </SelectTrigger>
                <SelectContent>
                  {availableUsers.map((u) => (
                    <SelectItem key={u.id} value={u.id}>
                      {u.name} — {u.email}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={() => addMemberMutation.mutate(selectedUserId)}
                disabled={!selectedUserId || addMemberMutation.isPending}
              >
                <UserPlus className="mr-2 h-4 w-4" />
                Add
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Danger Zone */}
      {isOrgAdmin && (
        <Card className="border-destructive/50">
          <CardHeader>
            <CardTitle className="text-destructive">Danger Zone</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Permanently delete this team and remove all its members.
            </p>
            <Button
              variant="destructive"
              onClick={() => setDeleteOpen(true)}
            >
              Delete Team
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Team</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete <strong>{team.name}</strong>? This
              cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteTeamMutation.mutate()}
              disabled={deleteTeamMutation.isPending}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
