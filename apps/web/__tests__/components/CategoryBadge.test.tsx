import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CategoryBadge } from "@/components/meetings/CategoryBadge";

describe("CategoryBadge", () => {
  it('renders "Work" label for work category', () => {
    render(<CategoryBadge category="work" />);
    expect(screen.getByText("Work")).toBeInTheDocument();
  });

  it('renders "Home" label for home category', () => {
    render(<CategoryBadge category="home" />);
    expect(screen.getByText("Home")).toBeInTheDocument();
  });

  it('renders "Private" label for private category', () => {
    render(<CategoryBadge category="private" />);
    expect(screen.getByText("Private")).toBeInTheDocument();
  });

  it("renders the raw category string for unknown categories", () => {
    render(<CategoryBadge category="unknown-cat" />);
    expect(screen.getByText("unknown-cat")).toBeInTheDocument();
  });

  it("applies blue colour class for work category", () => {
    const { container } = render(<CategoryBadge category="work" />);
    expect(container.firstChild).toHaveClass("bg-blue-100");
  });

  it("applies green colour class for home category", () => {
    const { container } = render(<CategoryBadge category="home" />);
    expect(container.firstChild).toHaveClass("bg-green-100");
  });

  it("applies purple colour class for private category", () => {
    const { container } = render(<CategoryBadge category="private" />);
    expect(container.firstChild).toHaveClass("bg-purple-100");
  });
});
