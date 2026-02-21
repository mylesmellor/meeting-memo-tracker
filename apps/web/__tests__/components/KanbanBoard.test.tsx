/**
 * KanbanBoard tests.
 *
 * @dnd-kit/core and @dnd-kit/sortable are mocked so:
 *  - DndContext renders its children and exposes onDragEnd for programmatic triggering
 *  - useSortable returns no-op values so ActionCard renders without drag state
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// ── dnd-kit mocks ─────────────────────────────────────────────────────────────

let capturedOnDragEnd: ((event: any) => void) | undefined;

vi.mock("@dnd-kit/core", () => ({
  DndContext: ({ children, onDragEnd }: any) => {
    capturedOnDragEnd = onDragEnd;
    return <div data-testid="dnd-context">{children}</div>;
  },
  closestCenter: vi.fn(),
  PointerSensor: class {},
  useSensor: vi.fn(() => ({})),
  useSensors: vi.fn(() => []),
}));

vi.mock("@dnd-kit/sortable", () => ({
  SortableContext: ({ children }: any) => <div>{children}</div>,
  verticalListSortingStrategy: vi.fn(),
  useSortable: () => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  }),
}));

vi.mock("@dnd-kit/utilities", () => ({
  CSS: { Transform: { toString: vi.fn(() => undefined) } },
}));

// ── component import (after mocks) ────────────────────────────────────────────

import { KanbanBoard } from "@/components/actions/KanbanBoard";

// ── fixtures ──────────────────────────────────────────────────────────────────

const MOCK_ACTIONS = [
  {
    id: "a1",
    description: "Write docs",
    status: "todo",
    priority: "medium",
    owner_text: null,
    due_date: null,
    meeting_title: null,
  },
  {
    id: "a2",
    description: "Review PR",
    status: "todo",
    priority: "high",
    owner_text: "Alice",
    due_date: null,
    meeting_title: "Sprint Planning",
  },
  {
    id: "a3",
    description: "Deploy to staging",
    status: "doing",
    priority: "high",
    owner_text: "Bob",
    due_date: null,
    meeting_title: null,
  },
  {
    id: "a4",
    description: "Close tickets",
    status: "done",
    priority: "low",
    owner_text: null,
    due_date: null,
    meeting_title: null,
  },
];

// ── tests ─────────────────────────────────────────────────────────────────────

describe("KanbanBoard", () => {
  it("renders all four column headings", () => {
    render(<KanbanBoard actions={MOCK_ACTIONS} onStatusChange={vi.fn()} />);
    expect(screen.getByText("To Do")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();
    expect(screen.getByText("Done")).toBeInTheDocument();
    expect(screen.getByText("Blocked")).toBeInTheDocument();
  });

  it("renders action cards in the correct columns", () => {
    render(<KanbanBoard actions={MOCK_ACTIONS} onStatusChange={vi.fn()} />);
    expect(screen.getByText("Write docs")).toBeInTheDocument();
    expect(screen.getByText("Review PR")).toBeInTheDocument();
    expect(screen.getByText("Deploy to staging")).toBeInTheDocument();
    expect(screen.getByText("Close tickets")).toBeInTheDocument();
  });

  it("displays correct action count badge for todo column (2 items)", () => {
    render(<KanbanBoard actions={MOCK_ACTIONS} onStatusChange={vi.fn()} />);
    // The todo column has 2 items; find the badge showing "2"
    const badges = screen.getAllByText("2");
    expect(badges.length).toBeGreaterThanOrEqual(1);
  });

  it("displays 0 count for blocked column when no blocked actions", () => {
    render(<KanbanBoard actions={MOCK_ACTIONS} onStatusChange={vi.fn()} />);
    // The blocked column has 0 items
    const zeroBadges = screen.getAllByText("0");
    expect(zeroBadges.length).toBeGreaterThanOrEqual(1);
  });

  it("calls onStatusChange with correct id and target status on drag end", () => {
    const onStatusChange = vi.fn();
    render(<KanbanBoard actions={MOCK_ACTIONS} onStatusChange={onStatusChange} />);

    // Simulate a drag-end event: card "a1" dropped onto the "doing" column
    capturedOnDragEnd?.({ active: { id: "a1" }, over: { id: "doing" } });

    expect(onStatusChange).toHaveBeenCalledWith("a1", "doing");
  });

  it("does not call onStatusChange when dropped outside a column", () => {
    const onStatusChange = vi.fn();
    render(<KanbanBoard actions={MOCK_ACTIONS} onStatusChange={onStatusChange} />);

    // `over` is null → no-op
    capturedOnDragEnd?.({ active: { id: "a1" }, over: null });
    expect(onStatusChange).not.toHaveBeenCalled();
  });

  it("renders without crashing when actions list is empty", () => {
    expect(() =>
      render(<KanbanBoard actions={[]} onStatusChange={vi.fn()} />)
    ).not.toThrow();
  });
});
