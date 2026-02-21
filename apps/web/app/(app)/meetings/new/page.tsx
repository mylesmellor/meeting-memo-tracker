"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TagInput } from "@/components/meetings/TagInput";
import { TranscriptUpload } from "@/components/meetings/TranscriptUpload";
import { toast } from "sonner";
import { ArrowLeft, ArrowRight } from "lucide-react";

interface Team {
  id: string;
  name: string;
}

export default function NewMeetingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [meetingId, setMeetingId] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<"work" | "home" | "private">("work");
  const [teamId, setTeamId] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const { data: teams } = useQuery({
    queryKey: ["teams"],
    queryFn: () => apiFetch<Team[]>("/api/v1/teams/"),
  });

  const handleStep1 = async () => {
    if (category === "work" && !teamId) {
      toast.error("Please select a team for work meetings");
      return;
    }
    setLoading(true);
    try {
      const data: any = await apiFetch<{ id: string }>("/api/v1/meetings/", {
        method: "POST",
        body: JSON.stringify({
          title: title || "Untitled Meeting",
          category,
          tags,
          team_id: teamId || null,
        }),
      });
      setMeetingId(data.id);
      setStep(2);
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  };

  const CATEGORIES = [
    { value: "work", label: "Work", description: "Requires a team" },
    { value: "home", label: "Home", description: "Personal / family" },
    { value: "private", label: "Private", description: "Confidential" },
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <div>
          <h1 className="text-2xl font-bold">New Meeting</h1>
          <p className="text-sm text-muted-foreground">Step {step} of 2</p>
        </div>
      </div>

      {/* Progress */}
      <div className="flex gap-2">
        <div className={`h-1.5 flex-1 rounded-full ${step >= 1 ? "bg-primary" : "bg-muted"}`} />
        <div className={`h-1.5 flex-1 rounded-full ${step >= 2 ? "bg-primary" : "bg-muted"}`} />
      </div>

      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Meeting Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title (optional — AI can suggest one)</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Q4 Strategy Review"
              />
            </div>

            <div className="space-y-2">
              <Label>Category</Label>
              <div className="grid grid-cols-3 gap-2">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat.value}
                    type="button"
                    onClick={() => setCategory(cat.value as any)}
                    className={`rounded-lg border p-3 text-left transition-colors ${
                      category === cat.value
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    <div className="font-medium text-sm">{cat.label}</div>
                    <div className="text-xs text-muted-foreground">{cat.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {category === "work" && (
              <div className="space-y-2">
                <Label htmlFor="team">Team *</Label>
                <select
                  id="team"
                  value={teamId}
                  onChange={(e) => setTeamId(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">Select a team...</option>
                  {teams?.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
            )}

            <div className="space-y-2">
              <Label>Tags</Label>
              <TagInput value={tags} onChange={setTags} category={category} />
            </div>

            <Button onClick={handleStep1} disabled={loading} className="w-full">
              {loading ? "Creating..." : "Continue"}
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      )}

      {step === 2 && meetingId && (
        <Card>
          <CardHeader>
            <CardTitle>Add Transcript</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <TranscriptUpload
              meetingId={meetingId}
              onSaved={() => router.push(`/meetings/${meetingId}`)}
            />
            <Button
              variant="ghost"
              className="w-full"
              onClick={() => router.push(`/meetings/${meetingId}`)}
            >
              Skip — Add transcript later
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
