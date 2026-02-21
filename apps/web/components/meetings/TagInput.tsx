"use client";

import { useState, useEffect } from "react";
import { X, Plus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { apiFetch } from "@/lib/api";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  category?: string;
}

export function TagInput({ value, onChange, category }: TagInputProps) {
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const presets = await apiFetch<string[]>(
          `/api/v1/tags/presets${category ? `?category=${category}` : ""}`
        );
        const recent = await apiFetch<string[]>(
          `/api/v1/tags/recent${category ? `?category=${category}` : ""}`
        );
        const combined = [...new Set([...recent, ...presets])];
        setSuggestions(combined.filter((t) => !value.includes(t)));
      } catch {
        // ignore
      }
    };
    load();
  }, [category, value]);

  const addTag = (tag: string) => {
    const trimmed = tag.trim().toLowerCase();
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }
    setInput("");
    setShowSuggestions(false);
  };

  const removeTag = (tag: string) => {
    onChange(value.filter((t) => t !== tag));
  };

  const filtered = suggestions.filter(
    (s) => s.toLowerCase().includes(input.toLowerCase()) && !value.includes(s)
  );

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1">
        {value.map((tag) => (
          <Badge key={tag} variant="secondary" className="text-xs">
            {tag}
            <button type="button" onClick={() => removeTag(tag)} className="ml-1">
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
      </div>
      <div className="relative">
        <Input
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setShowSuggestions(true);
          }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              if (input.trim()) addTag(input);
            }
            if (e.key === "Backspace" && !input && value.length > 0) {
              removeTag(value[value.length - 1]);
            }
          }}
          placeholder="Add tag..."
          className="h-8 text-sm"
        />
        {showSuggestions && filtered.length > 0 && (
          <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
            {filtered.slice(0, 8).map((s) => (
              <button
                key={s}
                type="button"
                className="w-full px-3 py-1.5 text-left text-sm hover:bg-accent"
                onMouseDown={() => addTag(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
