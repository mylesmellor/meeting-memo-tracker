/**
 * Tests for apiFetch and apiUpload.
 *
 * Strategy: stub global.fetch with vi.fn() so no real network calls are made.
 * The module is imported fresh for each test via vi.resetModules() where
 * needed, or we rely on vi.stubGlobal to replace fetch before import.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// We need to set the env var before importing the module so that API_BASE
// resolves to a known value.
vi.stubEnv("NEXT_PUBLIC_API_URL", "http://test-api");

// Dynamic import so we pick up the stubbed env.
const { apiFetch, apiUpload, ApiError } = await import("@/lib/api");

function makeFetchResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(body),
  };
}

describe("apiFetch", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns parsed JSON on 200", async () => {
    const mockFetch = vi.fn().mockResolvedValue(makeFetchResponse({ data: "ok" }));
    vi.stubGlobal("fetch", mockFetch);

    const result = await apiFetch("/api/v1/health");
    expect(result).toEqual({ data: "ok" });
  });

  it("returns undefined on 204 No Content", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
      json: vi.fn(),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await apiFetch("/api/v1/meetings/1", { method: "DELETE" });
    expect(result).toBeUndefined();
  });

  it("throws ApiError on 400", async () => {
    const mockFetch = vi
      .fn()
      .mockResolvedValue(makeFetchResponse({ detail: "Bad request" }, 400));
    vi.stubGlobal("fetch", mockFetch);

    await expect(apiFetch("/api/v1/bad")).rejects.toMatchObject({
      status: 400,
      message: "Bad request",
    });
  });

  it("throws ApiError on 500", async () => {
    const mockFetch = vi
      .fn()
      .mockResolvedValue(makeFetchResponse({ detail: "Server error" }, 500));
    vi.stubGlobal("fetch", mockFetch);

    await expect(apiFetch("/api/v1/crash")).rejects.toBeInstanceOf(ApiError);
  });

  it("on 401 calls refresh endpoint then retries original request", async () => {
    const mockFetch = vi
      .fn()
      // First call → 401 on the protected route
      .mockResolvedValueOnce(makeFetchResponse({ detail: "Unauthorised" }, 401))
      // Second call → refresh succeeds
      .mockResolvedValueOnce({ ok: true, status: 200, json: vi.fn().mockResolvedValue({}) })
      // Third call → retry succeeds
      .mockResolvedValueOnce(makeFetchResponse({ data: "retried" }));

    vi.stubGlobal("fetch", mockFetch);

    const result = await apiFetch("/api/v1/protected");
    expect(result).toEqual({ data: "retried" });

    // Three fetch calls total: original, refresh, retry
    expect(mockFetch).toHaveBeenCalledTimes(3);
    // Second call should be the refresh endpoint
    expect(mockFetch.mock.calls[1][0]).toContain("/api/v1/auth/refresh");
  });

  it("on 401 with failed refresh sets window.location.href to /auth/login", async () => {
    const mockFetch = vi
      .fn()
      // Protected route → 401
      .mockResolvedValueOnce(makeFetchResponse({ detail: "Unauthorised" }, 401))
      // Refresh → also fails
      .mockResolvedValueOnce({ ok: false, status: 401, json: vi.fn() });

    vi.stubGlobal("fetch", mockFetch);

    const locationMock = { href: "" };
    vi.stubGlobal("location", locationMock);

    await expect(apiFetch("/api/v1/protected")).rejects.toBeInstanceOf(ApiError);
    expect(locationMock.href).toBe("/auth/login");
  });
});

describe("apiUpload", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns parsed JSON on 200", async () => {
    const mockFetch = vi
      .fn()
      .mockResolvedValue(makeFetchResponse({ path: "/uploads/file.txt" }));
    vi.stubGlobal("fetch", mockFetch);

    const formData = new FormData();
    formData.append("file", new Blob(["content"]), "test.txt");

    const result = await apiUpload("/api/v1/meetings/1/transcript/upload", formData);
    expect(result).toEqual({ path: "/uploads/file.txt" });
  });

  it("throws ApiError on non-200 response", async () => {
    const mockFetch = vi
      .fn()
      .mockResolvedValue(makeFetchResponse({ detail: "File too large" }, 400));
    vi.stubGlobal("fetch", mockFetch);

    await expect(
      apiUpload("/api/v1/meetings/1/transcript/upload", new FormData())
    ).rejects.toMatchObject({ status: 400, message: "File too large" });
  });
});
