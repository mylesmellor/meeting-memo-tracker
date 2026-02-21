"use client";

import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface Version {
  id: string;
  version_num: number;
  status: string;
  redacted: boolean;
  created_at: string;
}

interface VersionListProps {
  versions: Version[];
  currentVersion: number;
  onSelect: (versionNum: number) => void;
}

export function VersionList({ versions, currentVersion, onSelect }: VersionListProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-muted-foreground">Version History</h3>
      {versions.map((v) => (
        <button
          key={v.id}
          onClick={() => onSelect(v.version_num)}
          className={`w-full text-left rounded-md border p-3 transition-colors hover:bg-accent ${
            v.version_num === currentVersion ? "border-primary bg-accent" : "border-border"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">v{v.version_num}</span>
            <div className="flex gap-1">
              {v.redacted && (
                <Badge variant="secondary" className="text-xs">Redacted</Badge>
              )}
              <Badge
                variant={v.status === "approved" ? "default" : "secondary"}
                className="text-xs"
              >
                {v.status}
              </Badge>
            </div>
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {format(new Date(v.created_at), "dd MMM yyyy HH:mm")}
          </div>
        </button>
      ))}
    </div>
  );
}
