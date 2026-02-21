const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${path}`;

  const res = await fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (res.status === 401) {
    // Try to refresh
    const refreshed = await tryRefresh();
    if (refreshed) {
      // Retry original request
      const retryRes = await fetch(url, {
        ...options,
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      });
      if (!retryRes.ok) {
        const err = await retryRes.json().catch(() => ({ detail: "Unknown error" }));
        throw new ApiError(retryRes.status, err.detail || "Request failed");
      }
      return retryRes.json();
    } else {
      // Redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }
      throw new ApiError(401, "Not authenticated");
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(res.status, err.detail || "Request failed");
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

export async function apiUpload<T>(
  path: string,
  formData: FormData
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    method: "POST",
    credentials: "include",
    body: formData,
    // Do NOT set Content-Type — browser sets it with boundary
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(res.status, err.detail || "Upload failed");
  }

  return res.json();
}
