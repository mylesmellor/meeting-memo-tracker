"use client";

import { useState, useEffect, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CategoryBadge } from "@/components/meetings/CategoryBadge";
import { TagList } from "@/components/meetings/TagList";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";
import { Plus, Search, CheckCircle2, Clock } from "lucide-react";

interface Meeting {
  id: string;
  title: string;
  category: string;
  tags: string[];
  status: string;
  action_count: number;
  created_at: string;
  latest_version_num: number | null;
}

const CATEGORIES = ["", "work", "home", "private"];

export default function MeetingsPage() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [category, setCategory] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const buildParams = () => {
    const p = new URLSearchParams();
    if (category) p.set("category", category);
    if (debouncedSearch) p.set("q", debouncedSearch);
    p.set("limit", "20");
    return p.toString();
  };

  const { data, isLoading } = useQuery({
    queryKey: ["meetings", category, debouncedSearch],
    queryFn: () => apiFetch<{ items: Meeting[]; total: number }>(`/api/v1/meetings/?${buildParams()}`),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Meetings</h1>
          <p className="text-muted-foreground">
            {data?.total ?? 0} meeting{data?.total !== 1 ? "s" : ""}
          </p>
        </div>
        <Button asChild>
          <Link href="/meetings/new">
            <Plus className="h-4 w-4 mr-2" />
            New Meeting
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search meetings..."
            className="pl-9"
          />
        </div>
        <div className="flex gap-1">
          {CATEGORIES.map((cat) => (
            <button
              key={cat || "all"}
              onClick={() => setCategory(cat)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                category === cat
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted hover:bg-accent"
              }`}
            >
              {cat ? cat.charAt(0).toUpperCase() + cat.slice(1) : "All"}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-20 w-full" />)}
        </div>
      ) : data?.items.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-muted-foreground mb-4">No meetings found</p>
          <Button asChild>
            <Link href="/meetings/new">
              <Plus className="h-4 w-4 mr-2" />
              Create your first meeting
            </Link>
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {data?.items.map((m) => (
            <Link
              key={m.id}
              href={`/meetings/${m.id}`}
              className="block rounded-lg border bg-card p-4 hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold truncate">{m.title}</h3>
                    <CategoryBadge category={m.category} />
                    {m.status === "approved" ? (
                      <span className="flex items-center gap-1 text-xs text-green-600">
                        <CheckCircle2 className="h-3 w-3" /> Approved
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-yellow-600">
                        <Clock className="h-3 w-3" /> Draft
                      </span>
                    )}
                  </div>
                  <div className="mt-2">
                    <TagList tags={m.tags} />
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xs text-muted-foreground">
                    {format(new Date(m.created_at), "dd MMM yyyy")}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {m.action_count} action{m.action_count !== 1 ? "s" : ""}
                    {m.latest_version_num && ` · v${m.latest_version_num}`}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
