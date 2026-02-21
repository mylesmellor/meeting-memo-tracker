import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AIOutput } from "@/components/meetings/AIOutput";

const FIXTURE_MARKDOWN = `# Q4 Planning Meeting

## Summary

- Budget approved for next quarter
- Timeline agreed by all teams

## Action Items

| # | Description | Owner | Due Date | Priority |
|---|-------------|-------|----------|----------|
| 1 | Set up CI/CD | Alice | 2025-03-01 | High |
| 2 | Write tests | — | — | Medium |

## Decisions

- Use React for the new frontend
`;

describe("AIOutput", () => {
  it("renders h1 heading from markdown", () => {
    render(<AIOutput markdown={FIXTURE_MARKDOWN} />);
    expect(screen.getByText("Q4 Planning Meeting")).toBeInTheDocument();
  });

  it("renders h2 section headings", () => {
    render(<AIOutput markdown={FIXTURE_MARKDOWN} />);
    expect(screen.getByText("Summary")).toBeInTheDocument();
    expect(screen.getByText("Action Items")).toBeInTheDocument();
    expect(screen.getByText("Decisions")).toBeInTheDocument();
  });

  it("renders list items from markdown", () => {
    render(<AIOutput markdown={FIXTURE_MARKDOWN} />);
    expect(screen.getByText("Budget approved for next quarter")).toBeInTheDocument();
    expect(screen.getByText("Use React for the new frontend")).toBeInTheDocument();
  });

  it("renders table content including column names", () => {
    // react-markdown without remark-gfm renders GFM tables as raw text —
    // the column names still appear in the document, just not as <th> elements.
    const { container } = render(<AIOutput markdown={FIXTURE_MARKDOWN} />);
    const text = container.textContent ?? "";
    expect(text).toContain("Description");
    expect(text).toContain("Owner");
    expect(text).toContain("Priority");
  });

  it("renders table row content", () => {
    const { container } = render(<AIOutput markdown={FIXTURE_MARKDOWN} />);
    const text = container.textContent ?? "";
    expect(text).toContain("Set up CI/CD");
    expect(text).toContain("Alice");
    expect(text).toContain("Write tests");
  });

  it("renders without crashing on empty string", () => {
    expect(() => render(<AIOutput markdown="" />)).not.toThrow();
  });
});
