import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface TagListProps {
  tags: string[];
  onRemove?: (tag: string) => void;
}

export function TagList({ tags, onRemove }: TagListProps) {
  if (!tags || tags.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1">
      {tags.map((tag) => (
        <Badge key={tag} variant="secondary" className="text-xs">
          {tag}
          {onRemove && (
            <button
              type="button"
              onClick={() => onRemove(tag)}
              className="ml-1 rounded-full hover:bg-muted-foreground/20"
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </Badge>
      ))}
    </div>
  );
}
