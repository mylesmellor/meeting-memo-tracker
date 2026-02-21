import { describe, expect, it } from "vitest";
import { cn } from "@/lib/utils";

describe("cn()", () => {
  it("merges class strings", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes — truthy included", () => {
    expect(cn("base", true && "active")).toContain("active");
  });

  it("handles conditional classes — falsy excluded", () => {
    const result = cn("base", false && "active");
    expect(result).not.toContain("active");
  });

  it("handles undefined and null without throwing", () => {
    expect(() => cn("a", undefined, null as any)).not.toThrow();
  });

  it("resolves Tailwind conflicts — later class wins", () => {
    // tailwind-merge should keep only 'p-4', dropping 'p-2'
    const result = cn("p-2", "p-4");
    expect(result).toBe("p-4");
    expect(result).not.toContain("p-2");
  });

  it("resolves Tailwind conflicts — text colour override", () => {
    const result = cn("text-red-500", "text-blue-500");
    expect(result).toBe("text-blue-500");
    expect(result).not.toContain("text-red-500");
  });

  it("returns empty string when no arguments", () => {
    expect(cn()).toBe("");
  });
});
