"use client";

import {
  DndContext,
  closestCenter,
  DragEndEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { ActionCard } from "./ActionCard";

interface ActionItem {
  id: string;
  description: string;
  owner_text: string | null;
  due_date: string | null;
  status: string;
  priority: string;
  meeting_title: string | null;
}

interface KanbanBoardProps {
  actions: ActionItem[];
  onStatusChange: (id: string, status: string) => void;
}

const COLUMNS = [
  { id: "todo", label: "To Do", color: "border-t-gray-400" },
  { id: "doing", label: "In Progress", color: "border-t-blue-500" },
  { id: "done", label: "Done", color: "border-t-green-500" },
  { id: "blocked", label: "Blocked", color: "border-t-red-500" },
];

export function KanbanBoard({ actions, onStatusChange }: KanbanBoardProps) {
  const sensors = useSensors(useSensor(PointerSensor));

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    // Find which column was dropped into
    const targetColumn = COLUMNS.find((col) => col.id === over.id);
    if (targetColumn) {
      onStatusChange(active.id as string, targetColumn.id);
    }
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {COLUMNS.map((col) => {
          const colActions = actions.filter((a) => a.status === col.id);
          return (
            <div
              key={col.id}
              className={`rounded-lg border border-t-4 ${col.color} bg-muted/30 p-3`}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold">{col.label}</h3>
                <span className="text-xs text-muted-foreground bg-background rounded-full px-2 py-0.5">
                  {colActions.length}
                </span>
              </div>
              <SortableContext
                id={col.id}
                items={colActions.map((a) => a.id)}
                strategy={verticalListSortingStrategy}
              >
                <div
                  id={col.id}
                  className="space-y-2 min-h-[4rem]"
                >
                  {colActions.map((action) => (
                    <ActionCard
                      key={action.id}
                      action={action}
                      onStatusChange={onStatusChange}
                    />
                  ))}
                </div>
              </SortableContext>
            </div>
          );
        })}
      </div>
    </DndContext>
  );
}
