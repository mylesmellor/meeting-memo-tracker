"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { format } from "date-fns";
import { CategoryBadge } from "@/components/meetings/CategoryBadge";
import { FileText, CheckSquare, AlertTriangle, Calendar } from "lucide-react";

interface Meeting {
  id: string;
  title: string;
  category: string;
  status: string;
  action_count: number;
  created_at: string;
  tags: string[];
}

interface ActionItem {
  id: string;
  description: string;
  due_date: string | null;
  status: string;
  priority: string;
  meeting_title: string;
}

export default function DashboardPage() {
  const today = new Date().toISOString().split("T")[0];
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];

  const { data: meetings, isLoading: loadingMeetings } = useQuery({
    queryKey: ["meetings", "recent"],
    queryFn: () => apiFetch<{ items: Meeting[]; total: number }>("/api/v1/meetings/?limit=5"),
  });

  const { data: overdueActions } = useQuery({
    queryKey: ["actions", "overdue"],
    queryFn: () => apiFetch<{ items: ActionItem[]; total: number }>("/api/v1/actions/?overdue=true&limit=10"),
  });

  const { data: thisWeekMeetings } = useQuery({
    queryKey: ["meetings", "this-week"],
    queryFn: () =>
      apiFetch<{ total: number }>(`/api/v1/meetings/?date_from=${weekAgo}&date_to=${today}&limit=1`),
  });

  const stats = [
    {
      title: "Total Meetings",
      value: meetings?.total ?? "—",
      icon: FileText,
      color: "text-blue-600",
    },
    {
      title: "Overdue Actions",
      value: overdueActions?.total ?? "—",
      icon: AlertTriangle,
      color: "text-red-600",
    },
    {
      title: "Meetings This Week",
      value: thisWeekMeetings?.total ?? "—",
      icon: Calendar,
      color: "text-green-600",
    },
    {
      title: "Pending Actions",
      value: overdueActions?.items.length ?? "—",
      icon: CheckSquare,
      color: "text-orange-600",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Overview of your meetings and actions</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Meetings */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Meetings</CardTitle>
            <Link href="/meetings" className="text-sm text-primary hover:underline">
              View all
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {loadingMeetings ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : meetings?.items.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">
              No meetings yet.{" "}
              <Link href="/meetings/new" className="text-primary hover:underline">
                Create your first one
              </Link>
            </p>
          ) : (
            <div className="space-y-3">
              {meetings?.items.map((m) => (
                <Link
                  key={m.id}
                  href={`/meetings/${m.id}`}
                  className="flex items-center justify-between rounded-md border p-3 hover:bg-accent transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <CategoryBadge category={m.category} />
                    <div>
                      <p className="text-sm font-medium">{m.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(m.created_at), "dd MMM yyyy")} · {m.action_count} actions
                      </p>
                    </div>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      m.status === "approved"
                        ? "bg-green-100 text-green-800"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {m.status}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Overdue Actions */}
      {overdueActions && overdueActions.items.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-red-600">Overdue Actions</CardTitle>
              <Link href="/actions?overdue=true" className="text-sm text-primary hover:underline">
                View all
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {overdueActions.items.slice(0, 5).map((a) => (
                <div key={a.id} className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 p-2">
                  <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm">{a.description}</p>
                    <p className="text-xs text-muted-foreground">
                      {a.meeting_title} · Due {a.due_date ? format(new Date(a.due_date), "dd MMM") : "—"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
