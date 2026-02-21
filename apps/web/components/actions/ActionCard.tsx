"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { format } from "date-fns";
import { GripVertical, Calendar, User, Flag } from "lucide-react";

interface ActionItem {
  id: string;
  description: string;
  owner_text: string | null;
  due_date: string | null;
  status: string;
  priority: string;
  meeting_title: string | null;
}

interface ActionCardProps {
  action: ActionItem;
  onStatusChange?: (id: string, status: string) => void;
}

const priorityColors = {
  high: "border-l-red-500",
  medium: "border-l-yellow-500",
  low: "border-l-gray-300",
};

export function ActionCard({ action, onStatusChange }: ActionCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: action.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`rounded-lg border-l-4 bg-card p-3 shadow-sm ${
        priorityColors[action.priority as keyof typeof priorityColors] || "border-l-gray-300"
      }`}
    >
      <div className="flex items-start gap-2">
        <button
          className="mt-0.5 text-muted-foreground hover:text-foreground cursor-grab"
          {...attributes}
          {...listeners}
        >
          <GripVertical className="h-4 w-4" />
        </button>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium leading-tight">{action.description}</p>
          {action.meeting_title && (
            <p className="text-xs text-muted-foreground mt-1 truncate">{action.meeting_title}</p>
          )}
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            {action.owner_text && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <User className="h-3 w-3" />
                {action.owner_text}
              </span>
            )}
            {action.due_date && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Calendar className="h-3 w-3" />
                {format(new Date(action.due_date), "dd MMM")}
              </span>
            )}
            <span
              className={`flex items-center gap-1 text-xs ${
                action.priority === "high"
                  ? "text-red-600"
                  : action.priority === "low"
                  ? "text-gray-500"
                  : "text-yellow-600"
              }`}
            >
              <Flag className="h-3 w-3" />
              {action.priority}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
