const fallbackBaseUrl = "/api/v1";

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? fallbackBaseUrl;

type ApiRequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  token?: string | null;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { body, headers, token, ...init } = options;
  const requestHeaders = new Headers(headers);
  requestHeaders.set("Accept", "application/json");
  const isFormDataBody = body instanceof FormData;

  if (body !== undefined && !isFormDataBody) {
    requestHeaders.set("Content-Type", "application/json");
  }

  if (token) {
    requestHeaders.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers: requestHeaders,
      body:
        body === undefined
          ? undefined
          : isFormDataBody
            ? body
            : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      0,
      "Не удалось связаться с сервером. Проверь доступность приложения и настройки API.",
    );
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (response.status === 204 || !contentType.includes("application/json")) {
    if (!response.ok) {
      throw new ApiError(response.status, await getResponseErrorMessage(response, "Request failed."));
    }
    return {} as T;
  }

  const payload = await response.json();
  if (!response.ok) {
    throw new ApiError(response.status, getErrorMessage(payload));
  }
  return payload as T;
}

export async function fetchBinary(path: string, token?: string | null): Promise<Blob> {
  const headers = new Headers();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: "GET",
    headers,
  });
  if (!response.ok) {
    throw new ApiError(response.status, await getResponseErrorMessage(response, "Не удалось открыть файл."));
  }
  return response.blob();
}

async function getResponseErrorMessage(
  response: Response,
  fallbackMessage: string,
): Promise<string> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    try {
      const payload = await response.json();
      const message = getErrorMessage(payload);
      if (message !== "Request failed.") {
        return message;
      }
    } catch {
      // fall through
    }
  }

  return response.status > 0 ? `${fallbackMessage} (HTTP ${response.status})` : fallbackMessage;
}

function getErrorMessage(payload: unknown): string {
  if (typeof payload === "string" && payload.trim()) {
    return payload;
  }

  if (
    typeof payload === "object" &&
    payload !== null &&
    "detail" in payload &&
    typeof payload.detail === "string"
  ) {
    return payload.detail;
  }

  return "Request failed.";
}
