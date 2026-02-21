"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  org_id: string;
}

interface Team {
  id: string;
  name: string;
  slug: string;
}

export default function SettingsPage() {
  const qc = useQueryClient();
  const [newPassword, setNewPassword] = useState("");

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<User>("/api/v1/auth/me"),
  });

  const { data: teams } = useQuery({
    queryKey: ["teams"],
    queryFn: () => apiFetch<Team[]>("/api/v1/teams/"),
  });

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Name</Label>
            <p className="mt-1 text-sm">{user?.name}</p>
          </div>
          <div>
            <Label>Email</Label>
            <p className="mt-1 text-sm">{user?.email}</p>
          </div>
          <div>
            <Label>Role</Label>
            <p className="mt-1 text-sm capitalize">{user?.role?.replace("_", " ")}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Teams</CardTitle>
        </CardHeader>
        <CardContent>
          {teams?.length === 0 ? (
            <p className="text-sm text-muted-foreground">No teams in your organisation yet</p>
          ) : (
            <ul className="space-y-1">
              {teams?.map((t) => (
                <li key={t.id} className="text-sm py-1 border-b last:border-0">
                  <Link
                    href={`/teams/${t.id}`}
                    className="hover:text-primary transition-colors"
                  >
                    {t.name}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
