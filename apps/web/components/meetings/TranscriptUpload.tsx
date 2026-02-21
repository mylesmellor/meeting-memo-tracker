"use client";

import { useState, useRef } from "react";
import { Upload, FileText } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { apiFetch, apiUpload } from "@/lib/api";
import { toast } from "sonner";

const MAX_CHARS = 50000;

interface TranscriptUploadProps {
  meetingId: string;
  onSaved: () => void;
}

export function TranscriptUpload({ meetingId, onSaved }: TranscriptUploadProps) {
  const [text, setText] = useState("");
  const [saving, setSaving] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const saveText = async () => {
    if (!text.trim()) return;
    setSaving(true);
    try {
      await apiFetch(`/api/v1/meetings/${meetingId}/transcript`, {
        method: "POST",
        body: JSON.stringify({ text }),
      });
      toast.success("Transcript saved");
      onSaved();
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    setSaving(true);
    try {
      await apiUpload(`/api/v1/meetings/${meetingId}/transcript/upload`, formData);
      toast.success("File uploaded and text extracted");
      onSaved();
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  };

  return (
    <Tabs defaultValue="paste">
      <TabsList>
        <TabsTrigger value="paste">Paste Text</TabsTrigger>
        <TabsTrigger value="upload">Upload File</TabsTrigger>
      </TabsList>

      <TabsContent value="paste" className="space-y-2">
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value.slice(0, MAX_CHARS))}
          placeholder="Paste your meeting transcript here..."
          className="h-64 resize-none font-mono text-sm"
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {text.length.toLocaleString()} / {MAX_CHARS.toLocaleString()} characters
          </span>
          <Button onClick={saveText} disabled={saving || !text.trim()} size="sm">
            {saving ? "Saving..." : "Save Transcript"}
          </Button>
        </div>
      </TabsContent>

      <TabsContent value="upload">
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-10 cursor-pointer transition-colors ${
            dragOver ? "border-primary bg-accent" : "border-border hover:border-primary"
          }`}
          onClick={() => fileRef.current?.click()}
        >
          <Upload className="h-10 w-10 text-muted-foreground mb-2" />
          <p className="text-sm font-medium">Drop a file here or click to upload</p>
          <p className="text-xs text-muted-foreground mt-1">Supports .txt, .md, .docx (max 10MB)</p>
          <input
            ref={fileRef}
            type="file"
            className="hidden"
            accept=".txt,.md,.docx"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) uploadFile(file);
            }}
          />
        </div>
      </TabsContent>
    </Tabs>
  );
}
