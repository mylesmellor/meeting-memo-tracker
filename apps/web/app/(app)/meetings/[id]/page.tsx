"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CategoryBadge } from "@/components/meetings/CategoryBadge";
import { TagList } from "@/components/meetings/TagList";
import { AIOutput } from "@/components/meetings/AIOutput";
import { VersionList } from "@/components/meetings/VersionList";
import { TranscriptUpload } from "@/components/meetings/TranscriptUpload";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { format } from "date-fns";
import {
  ArrowLeft, Sparkles, CheckCircle2, RotateCcw, ChevronDown, ChevronUp,
  Shield, Edit3
} from "lucide-react";
import Link from "next/link";

interface Version {
  id: string;
  version_num: number;
  rendered_markdown: string;
  ai_output_json: any;
  status: string;
  redacted: boolean;
  created_at: string;
}

interface ActionItem {
  id: string;
  description: string;
  owner_text: string | null;
  due_date: string | null;
  status: string;
  priority: string;
}

export default function MeetingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const qc = useQueryClient();

  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [showTranscript, setShowTranscript] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [redact, setRedact] = useState(false);

  const { data: meeting, isLoading } = useQuery({
    queryKey: ["meeting", id],
    queryFn: () => apiFetch<any>(`/api/v1/meetings/${id}`),
  });

  const { data: versions } = useQuery({
    queryKey: ["versions", id],
    queryFn: () => apiFetch<Version[]>(`/api/v1/meetings/${id}/versions`),
    enabled: !!meeting,
  });

  const { data: currentVersion } = useQuery({
    queryKey: ["version", id, selectedVersion ?? meeting?.latest_version_num],
    queryFn: () =>
      apiFetch<Version>(
        `/api/v1/meetings/${id}/versions/${selectedVersion ?? meeting?.latest_version_num}`
      ),
    enabled: !!(meeting && (selectedVersion ?? meeting?.latest_version_num)),
  });

  const { data: actions } = useQuery({
    queryKey: ["actions", id],
    queryFn: () =>
      apiFetch<{ items: ActionItem[] }>(`/api/v1/actions/?meeting_id=${id}&limit=50`),
    enabled: !!meeting,
  });

  const approveMutation = useMutation({
    mutationFn: (vNum: number) =>
      apiFetch(`/api/v1/meetings/${id}/versions/${vNum}/approve`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Version approved");
      qc.invalidateQueries({ queryKey: ["meeting", id] });
      qc.invalidateQueries({ queryKey: ["version", id] });
    },
    onError: (e: any) => toast.error(e.message),
  });

  const updateActionMutation = useMutation({
    mutationFn: ({ actionId, data }: { actionId: string; data: any }) =>
      apiFetch(`/api/v1/actions/${actionId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["actions", id] }),
    onError: (e: any) => toast.error(e.message),
  });

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await apiFetch(`/api/v1/meetings/${id}/generate?redact=${redact}`, { method: "POST" });
      toast.success("AI summary generated");
      qc.invalidateQueries({ queryKey: ["meeting", id] });
      qc.invalidateQueries({ queryKey: ["versions", id] });
      qc.invalidateQueries({ queryKey: ["actions", id] });
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!meeting) return null;

  const versionNum = selectedVersion ?? meeting.latest_version_num;

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-start gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.push("/meetings")} className="mt-1">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-2xl font-bold">{meeting.title}</h1>
            <CategoryBadge category={meeting.category} />
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                meeting.status === "approved"
                  ? "bg-green-100 text-green-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {meeting.status}
            </span>
          </div>
          <div className="flex items-center gap-3 mt-1">
            <TagList tags={meeting.tags} />
            <span className="text-xs text-muted-foreground">
              {format(new Date(meeting.created_at), "dd MMM yyyy")}
            </span>
          </div>
        </div>
      </div>

      {/* Transcript */}
      {meeting.transcript_text && (
        <Card>
          <CardHeader
            className="cursor-pointer"
            onClick={() => setShowTranscript(!showTranscript)}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Transcript</CardTitle>
              {showTranscript ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </div>
          </CardHeader>
          {showTranscript && (
            <CardContent>
              <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono max-h-64 overflow-y-auto">
                {meeting.transcript_text}
              </pre>
            </CardContent>
          )}
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main content */}
        <div className="lg:col-span-3 space-y-4">
          {!versionNum ? (
            <Card>
              <CardContent className="py-12 text-center space-y-4">
                <Sparkles className="h-12 w-12 text-muted-foreground mx-auto" />
                {!meeting.transcript_text ? (
                  <>
                    <p className="text-muted-foreground">Add a transcript first</p>
                    <TranscriptUpload
                      meetingId={id}
                      onSaved={() => qc.invalidateQueries({ queryKey: ["meeting", id] })}
                    />
                  </>
                ) : (
                  <>
                    <p className="text-muted-foreground">Ready to generate AI summary</p>
                    <div className="flex items-center justify-center gap-2">
                      <label className="flex items-center gap-2 text-sm cursor-pointer">
                        <input
                          type="checkbox"
                          checked={redact}
                          onChange={(e) => setRedact(e.target.checked)}
                          className="rounded"
                        />
                        <Shield className="h-3 w-3" />
                        Redact PII
                      </label>
                    </div>
                    <Button onClick={handleGenerate} disabled={generating}>
                      <Sparkles className="h-4 w-4 mr-2" />
                      {generating ? "Generating..." : "Generate AI Summary"}
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Generate controls */}
              <div className="flex items-center gap-2 flex-wrap">
                <label className="flex items-center gap-1.5 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={redact}
                    onChange={(e) => setRedact(e.target.checked)}
                    className="rounded"
                  />
                  <Shield className="h-3 w-3" />
                  Redact PII
                </label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGenerate}
                  disabled={generating || !meeting.transcript_text}
                >
                  <RotateCcw className="h-3 w-3 mr-1" />
                  {generating ? "Generating..." : "Regenerate"}
                </Button>
                {currentVersion && currentVersion.status !== "approved" && (
                  <Button
                    size="sm"
                    onClick={() => approveMutation.mutate(versionNum!)}
                    disabled={approveMutation.isPending}
                  >
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Approve v{versionNum}
                  </Button>
                )}
              </div>

              {/* AI Output */}
              {currentVersion ? (
                <Card>
                  <CardContent className="pt-6">
                    <AIOutput markdown={currentVersion.rendered_markdown} />
                  </CardContent>
                </Card>
              ) : (
                <Skeleton className="h-64 w-full" />
              )}
            </>
          )}

          {/* Action Items */}
          {actions && actions.items.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Action Items</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {actions.items.map((a) => (
                    <div key={a.id} className="flex items-center gap-3 rounded-md border p-2">
                      <select
                        value={a.status}
                        onChange={(e) =>
                          updateActionMutation.mutate({ actionId: a.id, data: { status: e.target.value } })
                        }
                        className="text-xs rounded border border-input bg-background px-2 py-1"
                      >
                        {["todo", "doing", "done", "blocked"].map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm">{a.description}</p>
                        {(a.owner_text || a.due_date) && (
                          <p className="text-xs text-muted-foreground">
                            {a.owner_text && `Owner: ${a.owner_text}`}
                            {a.owner_text && a.due_date && " · "}
                            {a.due_date && `Due: ${format(new Date(a.due_date), "dd MMM yyyy")}`}
                          </p>
                        )}
                      </div>
                      <span
                        className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                          a.priority === "high"
                            ? "bg-red-100 text-red-700"
                            : a.priority === "low"
                            ? "bg-gray-100 text-gray-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {a.priority}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Version sidebar */}
        {versions && versions.length > 0 && (
          <div className="lg:col-span-1">
            <VersionList
              versions={versions}
              currentVersion={versionNum ?? 0}
              onSelect={setSelectedVersion}
            />
          </div>
        )}
      </div>
    </div>
  );
}
